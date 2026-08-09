"""Groq (or any OpenAI-compatible) chat provider, grounded in the knowledge base.

Retrieved knowledge entries are injected into the system prompt, so the model
phrases and reasons about answers while the facts stay ours. When no key is
configured, or the call fails, the caller falls back to a local answer.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import requests
from django.conf import settings

from apps.chatbot.models import KnowledgeEntry
from apps.chatbot.services.knowledge import ROLE_LABELS, local_answer

logger = logging.getLogger(__name__)


@dataclass
class ProviderReply:
    answer: str
    provider: str
    model: str
    used_fallback: bool


def _config() -> tuple[str, str, str, str]:
    return (
        (getattr(settings, "CHATBOT_API_KEY", "") or "").strip(),
        (getattr(settings, "CHATBOT_API_URL", "") or "").strip(),
        (getattr(settings, "CHATBOT_PROVIDER", "Groq") or "Groq").strip(),
        (getattr(settings, "CHATBOT_MODEL", "") or "").strip(),
    )


def is_configured() -> bool:
    key, url, _, _ = _config()
    return bool(key and url)


def build_system_prompt(role: str, entries: list[KnowledgeEntry]) -> str:
    label = ROLE_LABELS.get(role, (role or "user").replace("_", " ").title())
    knowledge = "\n\n".join(f"### {e.title}\n{e.body}" for e in entries) or "(no matching entry)"
    return "\n".join(
        [
            "You are the in-app support assistant for the Kchekundu Hospital study and training platform.",
            f"The signed-in user's role is {label} ({role}).",
            "",
            "Rules:",
            "- Answer only from the knowledge below. Never invent page names, fields, buttons or rules.",
            "- If the knowledge does not cover the question, say so plainly and point the user to their admin "
            "or IT team. Do not guess.",
            "- When the user asks a conceptual question ('what is a change request?', 'why does this go to the "
            "HOD first?'), explain the concept in terms of this platform's actual workflow.",
            "- Be concise and practical: two short paragraphs at most, or a short numbered list of steps.",
            "- Use the real page names exactly as they appear in the knowledge.",
            "- Never claim to have read records, changed data, or completed an action. You cannot act.",
            "- Tailor the answer to the user's role; do not describe screens their role cannot open.",
            "",
            "Knowledge:",
            knowledge,
        ]
    )


def ask(
    *,
    question: str,
    role: str,
    history: list[dict[str, str]],
    entries: list[KnowledgeEntry],
) -> ProviderReply:
    key, url, provider, model = _config()
    if not key or not url:
        return ProviderReply(local_answer(question, role), provider, model or "local", True)

    convo: list[dict[str, str]] = [{"role": "system", "content": build_system_prompt(role, entries)}]
    for item in history[-8:]:
        if item.get("role") in {"user", "assistant"} and (item.get("text") or "").strip():
            convo.append({"role": item["role"], "content": item["text"].strip()})
    convo.append({"role": "user", "content": question})

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    referer = (getattr(settings, "CHATBOT_REFERER", "") or "").strip()
    title = (getattr(settings, "CHATBOT_TITLE", "") or "").strip()
    if referer:
        headers["HTTP-Referer"] = referer
    if title:
        headers["X-Title"] = title

    payload = {
        "model": model,
        "messages": convo,
        "temperature": getattr(settings, "CHATBOT_TEMPERATURE", 0.3),
        "max_tokens": getattr(settings, "CHATBOT_MAX_TOKENS", 500),
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=45)
        response.raise_for_status()
        data = response.json()
        answer = ((data.get("choices") or [{}])[0].get("message") or {}).get("content")
        if isinstance(answer, list):
            answer = "\n".join(
                part.get("text", "") if isinstance(part, dict) else str(part) for part in answer
            )
        answer = (answer or "").strip()
        if not answer:
            raise ValueError("Empty completion")
        return ProviderReply(answer, provider, model, False)
    except Exception:
        logger.exception("Chat provider request failed (%s, %s)", provider, model)
        return ProviderReply(local_answer(question, role), provider, model, True)

"""Draft the free-text fields users have to write by hand.

Every field in the platform that expects prose — a reason for study, a
reviewer's remarks, HR feedback to a university — is a place where people stall
on a blank box. These specs turn the surrounding form data into a first draft
the user then edits; nothing is submitted automatically.

The model is only ever allowed to phrase what the caller supplied. Facts come
from the form context, never from the model's own knowledge.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

MAX_CONTEXT_ITEMS = 25
MAX_CONTEXT_VALUE_CHARS = 600


@dataclass(frozen=True)
class FieldSpec:
    key: str
    label: str
    """Who the text is written as, and what it has to accomplish."""
    brief: str
    """Rough target so drafts match the field's expected weight."""
    words: str = "90-140 words"


FIELD_SPECS: dict[str, FieldSpec] = {
    "reason_for_study": FieldSpec(
        key="reason_for_study",
        label="Reason for study",
        brief=(
            "Write in the first person as the hospital staff member applying for further studies. "
            "Explain why the programme matters for their current role, what specific skills it adds, "
            "and how the hospital benefits when they return. Confident and professional, no flattery, "
            "no promises about funding or leave."
        ),
    ),
    "hr_feedback_for_university": FieldSpec(
        key="hr_feedback_for_university",
        label="HR feedback for the university",
        brief=(
            "Write as hospital HR addressing the student's university. State what was arranged for the "
            "placement and anything the university should know. Neutral, administrative, no praise or "
            "criticism of the student unless the context states it."
        ),
        words="60-100 words",
    ),
    "hod_note": FieldSpec(
        key="hod_note",
        label="Note to the Head of Department",
        brief=(
            "Write as hospital HR handing a placement to the receiving Head of Department. Say who is "
            "arriving, where, and anything the department must prepare. Brief and practical."
        ),
        words="40-80 words",
    ),
    "review_remarks": FieldSpec(
        key="review_remarks",
        label="Review remarks",
        brief=(
            "Write as the reviewer recording the reasoning behind their decision on this application. "
            "State the decision's basis against what the applicant submitted. Measured and factual; do "
            "not invent qualifications, dates or policy."
        ),
        words="60-110 words",
    ),
    "review_feedback_message": FieldSpec(
        key="review_feedback_message",
        label="Forwarding message",
        brief=(
            "Write as the reviewer forwarding a signed review report to the next stage. Say what is "
            "attached, what was concluded, and what is being asked of the recipient. Formal and short."
        ),
        words="50-90 words",
    ),
    "change_request_message": FieldSpec(
        key="change_request_message",
        label="Change request message",
        brief=(
            "Write as a reviewer asking the recipient to correct something in their application. Name "
            "what needs fixing and what a correct submission looks like. Direct, courteous, actionable; "
            "no blame."
        ),
        words="50-90 words",
    ),
    "semester_result_summary": FieldSpec(
        key="semester_result_summary",
        label="Result summary",
        brief=(
            "Write in the first person as the staff member reporting their semester results to their "
            "department. Summarise performance, notable coursework, and anything affecting progress. "
            "Factual; use only the marks and courses given."
        ),
        words="50-90 words",
    ),
    "hr_decision_reason": FieldSpec(
        key="hr_decision_reason",
        label="Decision reason",
        brief=(
            "Write as hospital HR stating the reason for accepting or rejecting this placement request. "
            "This text is quoted verbatim in the letter sent to the applicant, so it must stand alone, "
            "be respectful, and give a concrete reason."
        ),
        words="40-80 words",
    ),
}


class ComposeError(Exception):
    """Raised when a draft cannot be produced."""


def _context_block(context: dict[str, str]) -> str:
    lines: list[str] = []
    for key, value in list(context.items())[:MAX_CONTEXT_ITEMS]:
        text = (str(value) if value is not None else "").strip()
        if not text:
            continue
        lines.append(f"- {key}: {text[:MAX_CONTEXT_VALUE_CHARS]}")
    return "\n".join(lines) or "- (no details supplied)"


def build_prompt(spec: FieldSpec, context: dict[str, str], instruction: str, existing: str) -> list[dict]:
    system = "\n".join(
        [
            "You draft text for forms in a hospital study-and-training platform.",
            "",
            f"Field: {spec.label}.",
            spec.brief,
            "",
            "Hard rules:",
            "- Use ONLY the details supplied below. Never invent names, dates, grades, institutions "
            "or policies, and never write a placeholder like [Name] — omit what you were not given.",
            f"- Length: {spec.words}. Plain prose, no headings, no bullet points, no markdown.",
            "- No greeting, no sign-off, no subject line — this is the body of one form field.",
            "- Return the text only, with nothing before or after it.",
        ]
    )

    task = [f"Details:\n{_context_block(context)}"]
    if existing.strip():
        task.append(
            "The user already wrote this draft. Improve its clarity and tone while keeping every fact "
            f"and its intent:\n\"\"\"\n{existing.strip()[:2000]}\n\"\"\""
        )
    if instruction.strip():
        task.append(f"Extra instruction from the user: {instruction.strip()[:400]}")
    task.append("Write the field text now.")

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": "\n\n".join(task)},
    ]


def generate(*, field: str, context: dict[str, str], instruction: str = "", existing: str = "") -> str:
    spec = FIELD_SPECS.get(field)
    if spec is None:
        raise ComposeError("Unknown field.")

    api_key = (getattr(settings, "CHATBOT_API_KEY", "") or "").strip()
    url = (getattr(settings, "CHATBOT_API_URL", "") or "").strip()
    model = (getattr(settings, "CHATBOT_MODEL", "") or "").strip()
    if not api_key or not url:
        raise ComposeError("Text generation is not configured on this server.")

    payload = {
        "model": model,
        "messages": build_prompt(spec, context, instruction, existing),
        # Warmer than the assistant's factual Q&A: this is prose, and identical
        # wording on every regenerate would defeat the "try again" button.
        "temperature": 0.6,
        "max_tokens": 420,
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=45)
        response.raise_for_status()
        data = response.json()
        text = ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        if isinstance(text, list):
            text = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in text)
        text = text.strip().strip('"').strip()
        if not text:
            raise ComposeError("The generator returned nothing. Try again.")
        return text
    except ComposeError:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("Field text generation failed for %r", field)
        raise ComposeError("Could not reach the text generator. Try again in a moment.") from exc

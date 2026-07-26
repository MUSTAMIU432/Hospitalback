import logging
from typing import Optional

import requests
import strawberry
from django.conf import settings
from django.core.exceptions import ValidationError
from strawberry.types import Info

from apps.users.graphql.auth import require_auth
from core.constants import UserRole

logger = logging.getLogger(__name__)


@strawberry.input
class WorkflowChatHistoryInput:
    role: str
    text: str


@strawberry.type
class WorkflowChatReply:
    ok: bool
    answer: str
    provider: str
    model: str
    used_fallback: bool


ROLE_LABELS = {
    UserRole.STUDENT: "Student",
    UserRole.HOSPITAL_STAFF: "Hospital Staff",
    UserRole.HOD: "Head of Department",
    UserRole.ASST_DIRECTOR: "Assistant Director",
    UserRole.MANAGEMENT: "Top Management",
    UserRole.HOSPITAL_ADMIN: "Hospital Admin",
    UserRole.UNIV_ADMIN: "University Admin",
    UserRole.SYSADMIN: "System Admin",
    "hr": "HR Manager",
}

WORKFLOW_KNOWLEDGE_BASE = """
Platform:
- This system manages student field attachment requests and hospital staff further-studies applications.
- Further-studies review chain: Head of Department -> Assistant Director -> Top Management.
- Student field-attachment flow: Student submits -> HR reviews -> HR sends approved request to the selected department HOD.

Shared navigation:
- Left sidebar is role-based.
- The top-right bell opens Notifications.
- Settings includes account information and password change.

Student workflow:
- Students create field attachment requests from My Applications or Dashboard.
- They can save drafts, submit, track status, and download approval or rejection letters when available.
- Hospital-filled fields stay blank until HR processes the request.

Hospital staff workflow:
- Hospital staff uses Further studies application to create and submit a study request.
- Application tracking shows review stage.
- Change requests handles corrections.
- Application feedback shows final outcomes.
- Semester results lets staff send academic year and semester exam results to department/HOD.

HR workflow:
- Manage student field requests is the HR queue.
- HR can set the training site, add feedback, return, reject, or send the request to HOD.
- Department handoff shows requests already forwarded.

HOD workflow:
- Department results shows semester results submitted by staff for mapped departments.
- Approved student field requests shows HR-approved students for the HOD's department.
- Application review is the HOD queue for further-studies applications.
- HOD can send change requests and send review feedback to the Assistant Director.

Assistant Director workflow:
- Reviews HOD-forwarded staff applications and HOD feedback.
- Can send change requests and review feedback upward.

Top Management workflow:
- Final review stage for staff further-studies applications.
- Produces the final application report and approval/rejection outcome.

Hospital Admin workflow:
- Manages staff, positions, capabilities, roles, registry/imports, HOD assignments, and notifications.

University Admin workflow:
- Manages student registry, imports, and university registry.

System Admin workflow:
- Manages administrator accounts and system-wide admin access.
""".strip()


FALLBACK_ANSWERS = [
    {
        "keywords": ["semester", "exam result", "results"],
        "answer": "Hospital staff should open `Semester results` to send academic year and semester exam results to the department. HOD should open `Department results` to review staff submissions for mapped departments.",
    },
    {
        "keywords": ["notification", "bell", "message"],
        "answer": "Use the top-right bell or the `Notifications` sidebar item to read, filter, and reply to notifications.",
    },
    {
        "keywords": ["password", "login", "reset", "forgot"],
        "answer": "Use the login page for sign-in, `Forgot Password?` for reset, and `Settings` for password changes after you sign in.",
    },
    {
        "keywords": ["application", "further studies", "track", "change request"],
        "answer": "Hospital staff use `Further studies application` to submit, `Application tracking` to follow review stages, `Change requests` for corrections, and `Application feedback` for final outcomes.",
    },
]


def _normalize(text: str) -> str:
    return " ".join((text or "").lower().split())


def _fallback_answer(message: str) -> str:
    query = _normalize(message)
    for item in FALLBACK_ANSWERS:
        if any(keyword in query for keyword in item["keywords"]):
            return item["answer"]
    return (
        "I can help with this platform's workflows, pages, and roles. Try asking about `Semester results`, "
        "`Application tracking`, `Notifications`, `Manage student field requests`, or `Review Staff Application`."
    )


def _system_prompt(role: str) -> str:
    role_label = ROLE_LABELS.get(role, role.replace("_", " ").title() if role else "User")
    return (
        "You are the in-app support assistant for the Kchekundu study and training platform.\n"
        f"The authenticated user's role is: {role_label} ({role}).\n"
        "Only answer questions about this application's workflow, pages, roles, and operations.\n"
        "Give concise, practical, step-by-step answers using the real page names where possible.\n"
        "Do not invent data, do not claim to access records, and do not answer as if actions were already completed.\n"
        "If the question needs account-specific investigation, tell the user to contact their admin or IT team.\n"
        "If the question is outside this platform, say you only help with this application.\n\n"
        "Knowledge base:\n"
        f"{WORKFLOW_KNOWLEDGE_BASE}"
    )


@strawberry.type
class WorkflowChatMutation:
    @strawberry.mutation
    def workflow_chat(
        self,
        info: Info,
        message: str,
        history: Optional[list[WorkflowChatHistoryInput]] = None,
    ) -> WorkflowChatReply:
        user = require_auth(info)
        body = (message or "").strip()
        if not body:
            raise ValidationError("Message is required.")

        api_key = (getattr(settings, "CHATBOT_API_KEY", "") or "").strip()
        provider = (getattr(settings, "CHATBOT_PROVIDER", "OpenAI") or "OpenAI").strip()
        model = (getattr(settings, "CHATBOT_MODEL", "gpt-4o-mini") or "gpt-4o-mini").strip()
        endpoint = (getattr(settings, "CHATBOT_API_URL", "") or "").strip()

        if not api_key or not endpoint:
            return WorkflowChatReply(
                ok=True,
                answer=_fallback_answer(body),
                provider=provider,
                model=model,
                used_fallback=True,
            )

        convo = [{"role": "system", "content": _system_prompt(getattr(user, "role", ""))}]
        for item in (history or [])[-8:]:
            role = (item.role or "").strip().lower()
            if role not in {"user", "assistant"}:
                continue
            text = (item.text or "").strip()
            if not text:
                continue
            convo.append({"role": role, "content": text})
        convo.append({"role": "user", "content": body})

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
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
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            answer = ((data.get("choices") or [{}])[0].get("message") or {}).get("content")
            if isinstance(answer, list):
                answer = "\n".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in answer
                ).strip()
            answer = (answer or "").strip()
            if not answer:
                raise ValueError("Empty chat response")
            return WorkflowChatReply(
                ok=True,
                answer=answer,
                provider=provider,
                model=model,
                used_fallback=False,
            )
        except Exception:
            logger.exception("Workflow chat provider request failed")
            return WorkflowChatReply(
                ok=True,
                answer=_fallback_answer(body),
                provider=provider,
                model=model,
                used_fallback=True,
            )

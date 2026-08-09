"""Knowledge base for the in-app support assistant.

The seed entries below are the single source of truth about how this platform
works. They are synced into ``KnowledgeEntry`` rows on startup so admins can
edit them, and they are served to the frontend so the widget can answer
instantly (and offline) without a provider round-trip.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from apps.chatbot.models import KnowledgeEntry, KnowledgeSource

ALL_ROLES = [
    "student",
    "hospital_staff",
    "hr",
    "hod",
    "asst_director",
    "management",
    "hospital_admin",
    "univ_admin",
    "sysadmin",
]

ROLE_LABELS = {
    "student": "Student",
    "hospital_staff": "Hospital Staff",
    "hr": "HR Manager",
    "hod": "Head of Department",
    "asst_director": "Assistant Director",
    "management": "Top Management",
    "hospital_admin": "Hospital Admin",
    "univ_admin": "University Admin",
    "sysadmin": "System Admin",
}

STAFF_APPLICANT_ROLES = ["hospital_staff", "hod", "asst_director", "management"]


@dataclass(frozen=True)
class SeedEntry:
    key: str
    title: str
    body: str
    tags: list[str]
    roles: list[str] = field(default_factory=list)


SEED_ENTRIES: list[SeedEntry] = [
    # ── Platform overview ────────────────────────────────────────────────────
    SeedEntry(
        key="platform-overview",
        title="What this platform does",
        tags=["what is this", "platform", "system", "overview", "kchekundu", "about"],
        body=(
            "This is the Kchekundu Hospital study and training platform. It handles two request pipelines:\n"
            "1. Hospital staff further-studies applications, reviewed by Head of Department, then Assistant "
            "Director, then Top Management.\n"
            "2. Student field-attachment requests, reviewed by hospital HR and then handed to the department HOD.\n"
            "Everything else in the app (registries, staff records, capabilities, notifications, reports) exists "
            "to support those two pipelines."
        ),
    ),
    SeedEntry(
        key="navigation",
        title="Finding your way around",
        tags=["navigation", "sidebar", "menu", "where", "find page", "header", "search"],
        body=(
            "The left sidebar is role-based: it only lists what your role and capabilities allow. The top-right "
            "bell opens Notifications, the header holds the workspace switcher and dark-mode toggle, and the "
            "command palette (Ctrl+K / Cmd+K) jumps straight to any page you can reach. Settings holds your "
            "account information and password change."
        ),
    ),
    SeedEntry(
        key="login-password",
        title="Signing in, passwords and Google sign-in",
        tags=["login", "log in", "sign in", "password", "forgot", "reset", "google", "locked out", "signup"],
        body=(
            "Sign in with your username and password on the login page. If you forgot it, click 'Forgot "
            "Password?', enter your email, and follow the reset link sent to your inbox — the link expires, so "
            "request a fresh one if it has been sitting a while. Once signed in you change your password under "
            "Settings. Google sign-in only works when the Google account's email matches the email already on "
            "your platform account. If neither works, your hospital admin or IT team has to reset the account."
        ),
    ),
    SeedEntry(
        key="notifications",
        title="Notifications and replies",
        tags=["notification", "notifications", "bell", "unread", "message", "reply", "email"],
        body=(
            "Open the top-right bell or the Notifications sidebar item. You can read, filter, and mark messages "
            "as read, and reply directly where the sender allows it. Review decisions, change requests and "
            "forwarded applications all raise a notification, and some also send email when the site has email "
            "delivery switched on."
        ),
    ),

    # ── Further studies (staff) ──────────────────────────────────────────────
    SeedEntry(
        key="further-studies-apply",
        title="Applying for further studies",
        roles=STAFF_APPLICANT_ROLES,
        tags=["further studies", "apply", "new application", "study leave", "masters", "course", "scholarship"],
        body=(
            "Open 'Further studies application' and click New application. Fill in your applicant details, then "
            "Study information (institution and programme), then Study period (duration plus intended start and "
            "end dates), then your reason for study, and finally attach supporting documents. You can 'Save "
            "draft' at any point and finish later, or 'Save & submit' to send it into review. Once submitted the "
            "application becomes read-only unless a reviewer returns it to you."
        ),
    ),
    SeedEntry(
        key="programme-duration",
        title="Programme duration field",
        roles=STAFF_APPLICANT_ROLES,
        tags=["duration", "how long", "months", "years", "time", "period", "length", "yearly programme"],
        body=(
            "In the Study period section you must state how long the programme runs. Pick the unit first — "
            "Months or Years — then pick the count from the second dropdown (1-24 months, or 1-10 years). For a "
            "yearly programme choose Years and, for example, 2 years; for a short course choose Months. The "
            "duration is required before you can submit, it shows on the application detail page as 'Programme "
            "duration', and it is carried into the reviewer's report letter. Start and end dates stay optional "
            "and are separate from the duration."
        ),
    ),
    SeedEntry(
        key="further-studies-documents",
        title="Attaching documents to an application",
        roles=STAFF_APPLICANT_ROLES + ["student"],
        tags=["document", "upload", "attach", "file", "pdf", "admission letter", "crop", "delete document"],
        body=(
            "In the Supporting documents section pick a document type, then drag files onto the drop zone or "
            "browse for them. PDF, DOC, DOCX, PNG, JPG and WEBP are accepted. Images can be cropped before "
            "upload, staged files can be removed before saving, and on a draft you can delete already-uploaded "
            "documents. Files are stored with the application and travel with it through every review stage."
        ),
    ),
    SeedEntry(
        key="further-studies-tracking",
        title="Tracking a further-studies application",
        roles=STAFF_APPLICANT_ROLES,
        tags=["track", "tracking", "status", "stage", "where is my application", "progress", "pending"],
        body=(
            "'Application tracking' shows the current stage and the full review trail for each application. "
            "Stages run Head of Department, then Assistant Director, then Top Management. If you are a HOD "
            "applying for yourself the HOD stage is skipped; an Assistant Director's own application starts at "
            "Top Management. A returned application goes back to draft state so you can correct and resubmit it."
        ),
    ),
    SeedEntry(
        key="change-requests",
        title="Change requests",
        tags=["change request", "correction", "returned", "resubmit", "amend", "fix application"],
        body=(
            "A reviewer who needs something corrected sends a change request. Applicants see it under 'Change "
            "requests' and in notifications, with the reviewer's message and reply contact. Edit the application, "
            "then save and submit it again. Reviewers can also send internal change requests between Assistant "
            "Director and Top Management without returning the application to the applicant."
        ),
    ),
    SeedEntry(
        key="application-feedback",
        title="Reading the final decision",
        roles=STAFF_APPLICANT_ROLES,
        tags=["feedback", "decision", "approved", "rejected", "outcome", "final report", "letter"],
        body=(
            "'Application feedback' holds the final outcome and the signed letter produced by the reviewers. "
            "Top Management issues the final approval or rejection; the dispatch can be aimed at you, at your "
            "HOD, or at the Assistant Director, so the letter may reach you through your HOD. Approved letters "
            "can be downloaded as PDF from the application page."
        ),
    ),
    SeedEntry(
        key="semester-results",
        title="Sending semester exam results",
        roles=["hospital_staff", "hod"],
        tags=["semester", "exam", "results", "gpa", "average", "academic year", "study progress"],
        body=(
            "Staff on study leave report progress from 'Semester results': choose the department, academic year "
            "and semester, enter the exam average or GPA, add a short summary, then click 'Send to department'. "
            "Everything you have sent stays listed on that page. The HOD sees the same submissions under 'Staff "
            "progress' for the departments mapped to their account."
        ),
    ),

    # ── Student field attachment ─────────────────────────────────────────────
    SeedEntry(
        key="student-apply",
        title="Requesting a field attachment",
        roles=["student"],
        tags=["field", "attachment", "placement", "apply", "new application", "internship", "practical"],
        body=(
            "From My Applications or your dashboard click New application. Confirm your name, faculty, "
            "department, course and year of study, then fill the field attachment section: area where you intend "
            "to conduct the field, postal address, and the optional attachment start and end dates. Upload your "
            "official university field letter under Documents, then save a draft or submit the request to "
            "hospital HR."
        ),
    ),
    SeedEntry(
        key="student-profile",
        title="Completing your student profile",
        roles=["student"],
        tags=["profile", "registration number", "faculty", "department", "complete profile", "year of study"],
        body=(
            "New student accounts are asked to complete a profile before applying: names, registration number, "
            "programme, faculty, department, year of study and gender. Faculties and departments come from the "
            "University Registry, so if yours is missing the university admin has to add it. Edits you make on "
            "the application form are saved back to your profile."
        ),
    ),
    SeedEntry(
        key="student-waiting-hr",
        title="Blank hospital fields on a student request",
        roles=["student"],
        tags=["empty", "blank", "awaiting", "hr feedback", "training site", "field training conducted"],
        body=(
            "'Field training conducted at' and 'HR feedback' are filled in by hospital HR when they process your "
            "request, so they stay blank until then. That is normal for a request still sitting in the HR queue."
        ),
    ),
    SeedEntry(
        key="student-letters",
        title="Acceptance and rejection letters",
        roles=["student"],
        tags=["acceptance letter", "rejection letter", "download", "pdf", "approval letter"],
        body=(
            "Once HR decides, the application page offers a PDF download: an acceptance letter naming the "
            "confirmed training site and department, or a rejection letter carrying HR's stated reason. Both are "
            "generated by the system and can be re-downloaded at any time."
        ),
    ),

    # ── HR ───────────────────────────────────────────────────────────────────
    SeedEntry(
        key="hr-queue",
        title="Reviewing student field requests",
        roles=["hr", "hospital_admin"],
        tags=["hr", "field request", "queue", "review student", "accept", "reject", "return"],
        body=(
            "'Manage student field requests' is the HR queue. Open a request to confirm the training site, add HR "
            "feedback for the university, and then accept it into a department, return it for correction, or "
            "reject it with a reason. Set the confirmed training site before sending anything onward — the "
            "acceptance letter quotes it."
        ),
    ),
    SeedEntry(
        key="hr-handoff",
        title="Sending a student to the HOD",
        roles=["hr", "hospital_admin"],
        tags=["send to hod", "forward", "handoff", "department handoff", "placement"],
        body=(
            "Inside the review page choose the hospital department and click 'Send to HOD'. The request leaves "
            "the HR stage at that point and becomes read-only for HR. 'Department handoff' lists everything HR "
            "has already approved and forwarded, and the receiving HOD sees it under 'Approved student field "
            "requests'."
        ),
    ),

    # ── HOD / ADR / Management ───────────────────────────────────────────────
    SeedEntry(
        key="hod-review",
        title="HOD review workspace",
        roles=["hod"],
        tags=["hod", "review staff", "application review", "recommendation", "forward", "queue"],
        body=(
            "The HOD workspace holds four things: 'Application review' is the queue of further-studies "
            "applications from your department's staff; 'Send Change Request' asks the applicant for "
            "corrections; 'Send Review Feedback' forwards your signed recommendation to the Assistant Director; "
            "and 'Final Application Reports' keeps the review-report records. Applications only reach you when "
            "the applicant's staff profile is mapped to a department you head."
        ),
    ),
    SeedEntry(
        key="hod-department-views",
        title="HOD department views",
        roles=["hod"],
        tags=["staff progress", "department staff", "approved field requests", "department results"],
        body=(
            "'Staff progress' shows semester results submitted by staff in your mapped departments. 'Approved "
            "student field requests' shows students HR accepted into your department, with site and acceptance "
            "timing. 'Department staff' lists the people mapped to you."
        ),
    ),
    SeedEntry(
        key="adr-review",
        title="Assistant Director review",
        roles=["asst_director"],
        tags=["assistant director", "adr", "review", "hod feedback", "forward to management"],
        body=(
            "The Assistant Director reviews applications forwarded by HODs together with the HOD's "
            "recommendation. From there you can raise a change request (to the applicant, the HOD, or internally "
            "to Top Management) or send your own review feedback upward. The feedback-to-ADR workspace lets you "
            "compose the letter body and attach a signature before dispatch."
        ),
    ),
    SeedEntry(
        key="management-final",
        title="Top Management final decision",
        roles=["management"],
        tags=["top management", "final", "approve", "reject", "final report", "dispatch"],
        body=(
            "Top Management is the last stage for further-studies applications. You review the Assistant "
            "Director's feedback, produce the final application report, and dispatch the approval or rejection. "
            "The dispatch target decides who receives the letter first — the applicant, the HOD, or the "
            "Assistant Director."
        ),
    ),
    SeedEntry(
        key="review-chain",
        title="Who reviews what",
        tags=["who reviews", "chain", "stages", "workflow", "approval flow", "pipeline"],
        body=(
            "Further-studies applications: Head of Department, then Assistant Director, then Top Management. A "
            "reviewer applying for themselves skips their own stage. Student field-attachment requests: hospital "
            "HR first, then the HOD of the department HR selected. Every decision is written to the review trail "
            "on the application."
        ),
    ),

    # ── Admin surfaces ───────────────────────────────────────────────────────
    SeedEntry(
        key="hospital-admin",
        title="Hospital admin workspace",
        roles=["hospital_admin", "sysadmin"],
        tags=["hospital admin", "staff management", "positions", "hod assignment", "registry", "activity"],
        body=(
            "Hospital Admin runs the hospital-side setup: Staff Management (accounts and staff profiles), "
            "Position Management, Capability Management, Role Management, Registry & Imports, Activity and "
            "Notifications. HOD-to-department mappings live in the registry's HOD assignment area — an "
            "application cannot reach a HOD until that mapping exists."
        ),
    ),
    SeedEntry(
        key="capabilities",
        title="Capabilities and what a role can see",
        roles=["hospital_admin", "sysadmin", "management"],
        tags=["capability", "capabilities", "permission", "access", "empty page", "missing menu", "role"],
        body=(
            "Sidebar items and page access are driven by capabilities assigned to roles. If someone sees a menu "
            "item but the page is empty, the capability that grants the menu and the capability the queue "
            "filters on have drifted apart — check Capability Management and the role assignment page. Removing "
            "a capability hides the item immediately on the user's next load."
        ),
    ),
    SeedEntry(
        key="university-admin",
        title="University admin workspace",
        roles=["univ_admin", "sysadmin"],
        tags=["university", "student registry", "import students", "faculty", "department", "csv"],
        body=(
            "University Admin manages Student Registry (create students individually or import them in bulk) and "
            "University Registry (faculties and departments that populate the student and application "
            "dropdowns). Accepted field placements can also be reviewed from the university side."
        ),
    ),
    SeedEntry(
        key="imports",
        title="Bulk imports",
        roles=["univ_admin", "hospital_admin", "sysadmin"],
        tags=["import", "bulk", "csv", "excel", "batch", "upload students", "upload staff"],
        body=(
            "Registry & Imports accepts a spreadsheet and creates accounts in a batch. Each run is recorded as an "
            "import batch with its row counts and errors, so a partially failed import can be inspected and "
            "re-run after fixing the file."
        ),
    ),
    SeedEntry(
        key="sysadmin",
        title="System admin scope",
        roles=["sysadmin"],
        tags=["system admin", "sysadmin", "administrator", "create admin", "overview"],
        body=(
            "System Admin creates and manages administrator accounts and holds system-wide access. Use the "
            "sysadmin overview for a cross-hospital picture; day-to-day staff and student records still belong to "
            "the hospital and university admin workspaces."
        ),
    ),
    SeedEntry(
        key="assistant-scope",
        title="What this assistant can and cannot do",
        tags=["assistant", "chatbot", "help", "what can you do", "ai", "bot"],
        body=(
            "I explain how this platform works: pages, roles, workflows and the rules behind them. I cannot read "
            "your records, change data, approve anything, or act on your behalf, and I do not know account "
            "specifics such as why one particular application is stuck. For that, use the page itself or contact "
            "your admin or IT team."
        ),
    ),
]

SUGGESTIONS: dict[str, list[str]] = {
    "student": [
        "How do I create a field attachment request?",
        "Why are the hospital fields on my request empty?",
        "Where do I download my acceptance letter?",
    ],
    "hospital_staff": [
        "How do I apply for further studies?",
        "How do I set the programme duration?",
        "How do I track my application?",
    ],
    "hr": [
        "How do I review student field requests?",
        "How do I send a student to the HOD?",
        "Where is department handoff?",
    ],
    "hod": [
        "How do I review staff applications?",
        "Where do I see staff semester results?",
        "Where are approved student field requests?",
    ],
    "asst_director": [
        "How do I review HOD feedback?",
        "How do I send a change request?",
        "How do I forward feedback to Top Management?",
    ],
    "management": [
        "How do I issue the final decision?",
        "Where is the final application report?",
        "Who receives the dispatched letter?",
    ],
    "hospital_admin": [
        "How do I assign a HOD to a department?",
        "Why is a queue empty for a role?",
        "How do I manage capabilities?",
    ],
    "univ_admin": [
        "How do I import students?",
        "How do I add a faculty or department?",
        "Where is the student registry?",
    ],
    "sysadmin": [
        "How do I create administrator accounts?",
        "What does each admin role manage?",
        "How do I help someone locked out?",
    ],
}

GENERAL_SUGGESTIONS = [
    "How do I submit an application?",
    "Where do I see notifications?",
    "How do I reset my password?",
]


def suggestions_for(role: str) -> list[str]:
    return SUGGESTIONS.get(role, GENERAL_SUGGESTIONS)


# ── Sync & retrieval ─────────────────────────────────────────────────────────

def sync_seed_entries() -> int:
    """Upsert the built-in entries. Admin edits to title/body are overwritten on
    purpose — the code stays the source of truth for seed rows."""
    count = 0
    for entry in SEED_ENTRIES:
        KnowledgeEntry.objects.update_or_create(
            key=entry.key,
            defaults={
                "title": entry.title,
                "body": entry.body,
                "roles": ",".join(entry.roles),
                "tags": ",".join(entry.tags),
                "source": KnowledgeSource.SEED,
            },
        )
        count += 1
    return count


def ensure_seeded() -> None:
    """First-run convenience so a fresh database answers immediately.
    Re-syncing after that is an explicit `sync_chatbot_knowledge` call."""
    if not KnowledgeEntry.objects.filter(source=KnowledgeSource.SEED).exists():
        sync_seed_entries()


_WORD_RE = re.compile(r"[a-z0-9]+")

# Words too common in this domain to signal anything on their own.
_STOPWORDS = {
    "the", "a", "an", "is", "are", "do", "does", "did", "how", "what", "where", "when", "who", "why",
    "i", "my", "me", "you", "your", "it", "to", "for", "of", "on", "in", "and", "or", "can", "should",
    "this", "that", "with", "from", "at", "be", "have", "has", "get", "please", "help",
}


def _tokens(text: str) -> list[str]:
    return [w for w in _WORD_RE.findall((text or "").lower()) if w not in _STOPWORDS and len(w) > 1]


def keywords(text: str) -> list[str]:
    """Distinct, meaningful words — used to tag entries learned from chat."""
    return sorted(set(_tokens(text)))


def _score(entry: KnowledgeEntry, query: str, role: str) -> float:
    q = (query or "").lower()
    words = set(_tokens(query))
    if not words:
        return 0.0

    score = 0.0
    for tag in entry.tag_list:
        tag_l = tag.lower()
        # A multi-word tag appearing verbatim is the strongest possible signal.
        if " " in tag_l and tag_l in q:
            score += 6.0
        elif tag_l in words:
            score += 3.0

    title_words = set(_tokens(entry.title))
    score += 1.5 * len(words & title_words)

    body_words = set(_tokens(entry.body))
    score += 0.4 * len(words & body_words)

    if entry.role_list:
        # Role-specific entries win ties for that role and are demoted elsewhere.
        score += 2.0 if role in entry.role_list else -3.0
    return score


def search(query: str, role: str, *, limit: int = 4) -> list[KnowledgeEntry]:
    """Best-matching entries for a question, already filtered to the role."""
    ensure_seeded()
    entries = [e for e in KnowledgeEntry.objects.filter(is_active=True) if e.applies_to(role)]
    ranked = sorted(
        ((e, _score(e, query, role)) for e in entries),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return [entry for entry, score in ranked[:limit] if score > 0]


def entries_for_role(role: str) -> list[KnowledgeEntry]:
    """Everything the frontend may cache for local, offline answering."""
    ensure_seeded()
    return [e for e in KnowledgeEntry.objects.filter(is_active=True) if e.applies_to(role)]


def local_answer(query: str, role: str) -> str:
    """Deterministic answer used when no provider is configured or reachable."""
    hits = search(query, role, limit=2)
    if not hits:
        label = ROLE_LABELS.get(role, "user")
        return (
            f"I don't have that in the knowledge base yet. As a {label} you can ask me about applications, "
            "review stages, notifications, semester results, documents, or any page in your sidebar. If it is "
            "specific to your own account or records, your admin or IT team is the right next step."
        )
    if len(hits) == 1:
        return hits[0].body
    return f"{hits[0].body}\n\nRelated — {hits[1].title}:\n{hits[1].body}"

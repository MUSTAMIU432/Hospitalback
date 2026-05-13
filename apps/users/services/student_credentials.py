"""Default student credentials: username = registration number; password = first given name."""

from __future__ import annotations

from apps.students.models import StudentProfile
from apps.users.models import User

from core.constants import UserRole


def student_default_password_from_full_name(full_name: str) -> str:
    """First whitespace-separated token of *full_name* (the given first name for login)."""
    s = (full_name or "").strip()
    if not s:
        return ""
    return s.split()[0]


def student_default_password_token(*, profile: StudentProfile, user: User) -> str:
    """Token used as default password: prefer profile.full_name, else User.first_name."""
    for source in (getattr(profile, "full_name", None) or "", user.first_name or ""):
        tok = student_default_password_from_full_name(source)
        if tok:
            return tok
    return ""


def student_default_password_matches_plain(
    *, profile: StudentProfile, user: User, password: str
) -> bool:
    """
    True if *password* matches the student's default (first name) token.

    Accepts exact match to the stored token, or case-insensitive match so existing
    rows still work when casing differs from what the user types.
    """
    if not password:
        return False
    expected = student_default_password_token(profile=profile, user=user)
    if not expected:
        return False
    if password == expected:
        return True
    if password.casefold() == expected.casefold():
        return True
    return False


def student_login_password_ok(*, user: User, profile: StudentProfile, password: str) -> bool:
    """True if *password* is valid for this student (stored hash or default first-name rule)."""
    if not user.is_active or user.role != UserRole.STUDENT:
        return False
    if user.check_password(password):
        return True
    return student_default_password_matches_plain(profile=profile, user=user, password=password)

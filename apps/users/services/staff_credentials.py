"""Hospital staff sign-in: stored password, or default first given name from profile.full_name (legacy: national ID)."""

from __future__ import annotations

from apps.employees.models import HospitalStaff
from apps.users.models import User
from apps.users.services.student_credentials import student_default_password_from_full_name
from core.constants import UserRole


def hospital_staff_login_password_ok(*, user: User, profile: HospitalStaff, password: str) -> bool:
    """True if *password* is valid (hashed password, default first-name token, or legacy national ID)."""
    if not user.is_active or user.role != UserRole.HOSPITAL_STAFF:
        return False
    if user.check_password(password):
        return True
    tok = student_default_password_from_full_name(profile.full_name or "")
    if tok and (password == tok or password.casefold() == tok.casefold()):
        return True
    nid = (profile.national_id or "").strip()
    if nid and password == nid:
        return True
    return False

from __future__ import annotations

from apps.employees.models import HospitalStaff, StaffCapabilityOverride, StaffRoleCapability
from core.constants import HOSPITAL_WORKER_ROLES, UserRole


def staff_capabilities_for_user(user) -> list[str]:
    if getattr(user, "role", None) not in HOSPITAL_WORKER_ROLES:
        return []
    prof = getattr(user, "hospital_staff_profile", None)
    if not prof:
        return []
    role_caps = set(
        StaffRoleCapability.objects.filter(
            role_id=prof.staff_role_id,
            is_active=True,
            capability__is_active=True,
        ).values_list("capability__code", flat=True)
    )
    for ov in StaffCapabilityOverride.objects.filter(staff=prof, is_active=True, capability__is_active=True):
        code = ov.capability.code
        if ov.mode == StaffCapabilityOverride.MODE_GRANT:
            role_caps.add(code)
        else:
            role_caps.discard(code)
    if not role_caps and prof.capabilities:
        # Fallback for legacy rows while migrating.
        role_caps.update(prof.capabilities)
    return sorted(role_caps)


def user_has_staff_capability(user, capability: str) -> bool:
    return capability in staff_capabilities_for_user(user)


def users_with_staff_capability(capability: str):
    """Active users (hospital_staff role) whose roster row includes the capability."""
    out: list = []
    for row in HospitalStaff.objects.select_related("user").filter(user__is_active=True):
        u = row.user
        if getattr(u, "role", None) == UserRole.HOSPITAL_STAFF and capability in staff_capabilities_for_user(u):
            out.append(u)
    return out

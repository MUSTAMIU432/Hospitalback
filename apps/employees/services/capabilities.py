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


# A few permissions exist under two code names: the legacy reviewer-flow code
# (``*_assess_details``) and the current hub code (``*_hub_app_review``). They mean
# the same thing — "review staff applications at this stage" — so holding either
# satisfies a check for the other. Capability-driven reviewers are provisioned
# with the hub codes, while older backend gates ask for the assess_details codes.
_CAP_EQUIVALENTS: dict[str, set[str]] = {
    "hod_assess_details": {"hod_assess_details", "hod_hub_app_review"},
    "hod_hub_app_review": {"hod_assess_details", "hod_hub_app_review"},
    "adr_assess_details": {"adr_assess_details", "adr_hub_app_review"},
    "adr_hub_app_review": {"adr_assess_details", "adr_hub_app_review"},
}


def user_has_staff_capability(user, capability: str) -> bool:
    have = set(staff_capabilities_for_user(user))
    wanted = _CAP_EQUIVALENTS.get(capability, {capability})
    return bool(have & wanted)


def users_with_staff_capability(capability: str):
    """Active users (hospital_staff role) whose roster row includes the capability."""
    out: list = []
    for row in HospitalStaff.objects.select_related("user").filter(user__is_active=True):
        u = row.user
        if getattr(u, "role", None) == UserRole.HOSPITAL_STAFF and capability in staff_capabilities_for_user(u):
            out.append(u)
    return out

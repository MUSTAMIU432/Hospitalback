"""Map a user onto the assistant's role vocabulary.

HR is a capability on a `hospital_staff` account rather than its own role, but
the knowledge base talks about it as a role — so resolve it here, once.
"""

from apps.employees.services.capabilities import user_has_staff_capability
from core.constants import StaffCapability, UserRole


def chat_role_for(user) -> str:
    role = getattr(user, "role", "") or ""
    if role == UserRole.HOSPITAL_STAFF and user_has_staff_capability(
        user, StaffCapability.HR_FIELD_REQUESTS.value
    ):
        return "hr"
    return role or "hospital_staff"

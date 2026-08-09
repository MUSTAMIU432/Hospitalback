import strawberry
import strawberry_django

from apps.users.models import User
from core.constants import UserRole


@strawberry_django.type(
    User,
    exclude=["password", "groups", "user_permissions"],
    fields=[
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "module",
        "is_first_login",
        "is_active",
        "is_staff",
        "created_at",
        "last_login",
    ],
)
class UserType:
    @strawberry.field
    def photo_url(self, root: User) -> str:
        """Media path of the profile picture, or "" when none is set.

        Returned as a path (not an absolute URL) to match how the SPA already
        resolves application documents against the backend origin.
        """
        photo = getattr(root, "photo", None)
        if not photo:
            return ""
        try:
            return photo.url
        except ValueError:
            return ""

    @strawberry.field
    def staff_capabilities(self, root: User) -> list[str]:
        from apps.employees.services.capabilities import staff_capabilities_for_user

        return staff_capabilities_for_user(root)

    @strawberry.field
    def profile_complete(self, root: User) -> bool:
        """False only for a student who has not filled in their StudentProfile yet.

        Lives on the user rather than behind its own query so the SPA learns it
        from the `me` / `login` payload it already fetches — the profile gate can
        then redirect on the first render, with no second round-trip and no
        flash of the dashboard before the redirect lands.
        """
        from apps.students.services.self_profile import profile_is_complete

        return profile_is_complete(root)

    @strawberry.field
    def profile_title(self, root: User) -> str:
        """Human-friendly identity title shown under user name in the UI."""
        profile = getattr(root, "hospital_staff_profile", None)
        department_name = getattr(getattr(profile, "department", None), "name", "") or ""
        staff_role_name = getattr(getattr(profile, "staff_role", None), "name", "") or ""
        role = getattr(root, "role", "")

        if role == UserRole.HOD:
            if department_name:
                return f"Head of {department_name}"
            return staff_role_name or "Head of Department"
        if role == UserRole.ASST_DIRECTOR:
            return staff_role_name or "Assistant Director"
        if role == UserRole.MANAGEMENT:
            return staff_role_name or "Top Management"
        if role == UserRole.HOSPITAL_ADMIN:
            return staff_role_name or "Hospital Administrator"
        if role == UserRole.UNIV_ADMIN:
            return "University Administrator"
        if role == UserRole.STUDENT:
            return "Student"
        if role == UserRole.SYSADMIN:
            return "System Administrator"
        if role == UserRole.HOSPITAL_STAFF:
            if staff_role_name:
                return staff_role_name
            if department_name:
                return f"Staff - {department_name}"
            return "Hospital Staff"
        return role.replace("_", " ").title() if role else "User"


@strawberry.type
class AuthPayload:
    access_token: str
    refresh_token: str
    token_type: str
    user: UserType


@strawberry.type
class OperationResult:
    ok: bool
    message: str

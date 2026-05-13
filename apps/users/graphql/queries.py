import strawberry
from django.core.exceptions import PermissionDenied
from strawberry.types import Info

from apps.users.graphql.auth import require_auth
from apps.users.graphql.types import UserType
from apps.users.models import User
from core.constants import UserRole
from strawberry_django.auth.utils import get_current_user


@strawberry.type
class UsersQuery:
    @strawberry.field
    def me(self, info: Info) -> UserType | None:
        user = get_current_user(info, strict=False)
        if not user.is_authenticated:
            return None
        return User.objects.get(pk=user.pk)

    @strawberry.field
    def tenant_admins(self, info: Info) -> list[UserType]:
        """Hospital and university administrators — visible only to system administrators."""
        user = require_auth(info)
        if getattr(user, "role", None) != UserRole.SYSADMIN:
            raise PermissionDenied("Not allowed.")
        return list(
            User.objects.filter(role__in=(UserRole.HOSPITAL_ADMIN, UserRole.UNIV_ADMIN)).order_by(
                "username"
            )
        )

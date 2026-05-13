from django.core.exceptions import PermissionDenied
from strawberry.types import Info

from apps.users.models import User
from strawberry_django.auth.utils import get_current_user


def require_auth(info: Info) -> User:
    user = get_current_user(info, strict=False)
    if not user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    return user

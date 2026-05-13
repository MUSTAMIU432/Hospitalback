import strawberry
from strawberry.types import Info

from apps.notifications.graphql.types import NotificationType
from apps.notifications.models import Notification
from apps.users.graphql.auth import require_auth


@strawberry.type
class NotificationsQuery:
    @strawberry.field
    def my_notifications(self, info: Info, unread_only: bool = False) -> list[NotificationType]:
        user = require_auth(info)
        qs = Notification.objects.filter(recipient=user)
        if unread_only:
            qs = qs.filter(is_read=False)
        return list(qs[:200])

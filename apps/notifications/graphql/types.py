from django.db.models import Q
import strawberry_django

from apps.notifications.models import Notification
from apps.users.graphql.types import UserType


@strawberry_django.type(
    Notification,
    fields=[
        "id",
        "message",
        "destination_path",
        "is_read",
        "notif_type",
        "created_at",
    ],
)
class NotificationType:
    @strawberry_django.field()
    def sender(self, root: Notification) -> UserType | None:
        if root.sender_id is None:
            return None
        from apps.users.models import User
        return User.objects.filter(pk=root.sender_id).first()

    @strawberry_django.field()
    def recipient(self, root: Notification) -> UserType:
        from apps.users.models import User
        return User.objects.get(pk=root.recipient_id)

    @strawberry_django.field()
    def parent_id(self, root: Notification) -> str | None:
        return str(root.parent_id) if root.parent_id else None

    @strawberry_django.field()
    def thread(self, root: Notification) -> list["NotificationType"]:
        """All messages in this conversation thread (root + all replies), oldest first."""
        root_id = root.parent_id if root.parent_id else root.id
        return list(
            Notification.objects.filter(
                Q(id=root_id) | Q(parent_id=root_id)
            )
            .select_related("sender", "recipient")
            .order_by("created_at")
        )

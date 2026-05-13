import uuid
from typing import Optional

import strawberry
from django.core.exceptions import PermissionDenied, ValidationError
from strawberry.types import Info

from apps.notifications.graphql.types import NotificationType
from apps.notifications.models import Notification
from apps.notifications.services.notify import notify_user, notify_users
from apps.users.graphql.auth import require_auth
from core.constants import HOSPITAL_WORKER_ROLES, NotificationType as NT, UserRole


@strawberry.type
class NotificationsMutation:
    @strawberry.mutation
    def mark_notification_read(self, info: Info, notification_id: uuid.UUID) -> NotificationType:
        user = require_auth(info)
        notif = Notification.objects.get(pk=notification_id, recipient=user)
        notif.is_read = True
        notif.save(update_fields=["is_read"])
        return notif

    @strawberry.mutation
    def delete_notification(self, info: Info, notification_id: uuid.UUID) -> bool:
        user = require_auth(info)
        notif = Notification.objects.get(pk=notification_id, recipient=user)
        notif.delete()
        return True

    @strawberry.mutation
    def reply_notification(
        self,
        info: Info,
        notification_id: uuid.UUID,
        message: str,
        notif_type: str = NT.REVISION,
        destination_path: Optional[str] = strawberry.UNSET,
    ) -> NotificationType:
        actor = require_auth(info)
        original = Notification.objects.select_related("sender", "recipient").get(
            pk=notification_id, recipient=actor
        )
        body = (message or "").strip()
        if not body:
            raise ValidationError("Reply message is required.")
        if not original.sender_id:
            raise ValidationError("This notification has no sender to reply to.")
        valid_types = {c[0] for c in NT.choices}
        if notif_type not in valid_types:
            raise ValidationError(f"Invalid notif_type '{notif_type}'.")
        dest = (
            destination_path.strip()
            if destination_path is not strawberry.UNSET and destination_path and destination_path.strip()
            else (original.destination_path or "")
        )
        # The thread root is the original's parent (if it's already a reply) or the original itself
        thread_root_id = original.parent_id if original.parent_id else original.id
        reply = Notification.objects.create(
            recipient=original.sender,
            sender=actor,
            message=body,
            notif_type=notif_type,
            destination_path=dest,
            parent_id=thread_root_id,
        )
        # Mark the original as read since the recipient has now replied
        if not original.is_read:
            original.is_read = True
            original.save(update_fields=["is_read"])
        return reply

    @strawberry.mutation
    def send_notification(
        self,
        info: Info,
        message: str,
        notif_type: str,
        recipient_username: Optional[str] = strawberry.UNSET,
        recipient_role: Optional[str] = strawberry.UNSET,
        destination_path: Optional[str] = strawberry.UNSET,
    ) -> list[NotificationType]:
        """
        Send a notification to:
          - a single user by username (recipient_username), or
          - all active users in a role (recipient_role), or
          - all active hospital-worker users (both omitted).
        Only hospital_admin and sysadmin may send.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        actor = require_auth(info)
        if getattr(actor, "role", None) not in (UserRole.HOSPITAL_ADMIN, UserRole.SYSADMIN):
            if not (recipient_username and recipient_username is not strawberry.UNSET and recipient_username.strip()):
                raise PermissionDenied("Only hospital admin or sysadmin can broadcast notifications.")

        message = (message or "").strip()
        if not message:
            raise ValidationError("Message is required.")

        valid_types = {c[0] for c in NT.choices}
        if notif_type not in valid_types:
            raise ValidationError(f"Invalid notif_type '{notif_type}'.")

        # Resolve recipients
        if recipient_username and recipient_username is not strawberry.UNSET and recipient_username.strip():
            try:
                target = User.objects.get(username=recipient_username.strip())
            except User.DoesNotExist as exc:
                raise ValidationError(f"User '{recipient_username}' not found.") from exc
            recipients = [target]
        elif recipient_role and recipient_role is not strawberry.UNSET and recipient_role.strip():
            recipients = list(User.objects.filter(role=recipient_role.strip(), is_active=True))
            if not recipients:
                raise ValidationError(f"No active users with role '{recipient_role}'.")
        else:
            # Broadcast to all active hospital workers
            recipients = list(User.objects.filter(role__in=HOSPITAL_WORKER_ROLES, is_active=True))

        dest = (
            destination_path.strip()
            if destination_path is not strawberry.UNSET and destination_path and destination_path.strip()
            else ""
        )
        return notify_users(
            recipients=recipients,
            message=message,
            notif_type=notif_type,
            destination_path=dest,
            sender=actor,
        )

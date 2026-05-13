import uuid

from django.conf import settings
from django.db import models

from core.constants import NotificationType


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications_sent",
    )
    message = models.TextField()
    destination_path = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Optional frontend route to open when user clicks notification.",
    )
    is_read = models.BooleanField(default=False)
    notif_type = models.CharField(max_length=50, choices=NotificationType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
        help_text="Root notification this message is a reply to (null = root).",
    )

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["parent"]),
        ]

    def __str__(self) -> str:
        return f"{self.recipient_id}: {self.notif_type}"

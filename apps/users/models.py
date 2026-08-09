import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants import UserModule, UserRole


def profile_photo_upload_to(instance: "User", filename: str) -> str:
    """One folder per user so replacing a photo never collides with another's."""
    safe = filename.replace("..", "").replace("/", "_")
    return f"profile-photos/{instance.pk}/{safe}"


class User(AbstractUser):
    """Central authentication record (STUD spec)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        _("username"),
        max_length=50,
        unique=True,
        help_text=_("Employee number or student registration number."),
    )
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.HOSPITAL_STAFF,
    )
    module = models.CharField(
        max_length=30,
        choices=UserModule.choices,
        default=UserModule.FURTHER_STUDIES,
    )
    is_first_login = models.BooleanField(default=True)
    photo = models.ImageField(
        upload_to=profile_photo_upload_to,
        blank=True,
        null=True,
        help_text=_("Profile picture shown in the header and on the account page."),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
        ordering = ["username"]

    def save(self, *args, **kwargs):
        # Django superusers (createsuperuser / is_superuser) map to STUD platform admin.
        if self.is_superuser:
            self.role = UserRole.SYSADMIN
            self.module = UserModule.ADMIN
            self.is_staff = True
            self.is_first_login = False
        elif self.role in (
            UserRole.SYSADMIN,
            UserRole.HOSPITAL_ADMIN,
        ):
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username


class PasswordResetToken(models.Model):
    """A single-use, time-limited password reset grant.

    Only the SHA-256 hash of `email:code` is stored: a leaked database dump must
    not let an attacker replay a reset. The six-digit code exists only in the
    email we send and in what the user types back.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(
        default=0,
        help_text="Wrong-code submissions against this grant; the code burns at the limit.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # Recorded for abuse investigation — reset endpoints are a common spray target.
    requested_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "password_reset_tokens"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"reset for {self.user.username} (expires {self.expires_at:%Y-%m-%d %H:%M})"

    @property
    def is_usable(self) -> bool:
        from django.utils import timezone

        return self.used_at is None and self.expires_at > timezone.now()


class GoogleIdentity(models.Model):
    """Links a Google account to a STUD user.

    Keyed on Google's `sub` claim, not email: email addresses can be changed or
    reassigned, `sub` is a stable per-account identifier. Storing it means a
    user who later changes their Google email still resolves to the same record.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="google_identity")
    google_sub = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "google_identities"

    def __str__(self) -> str:
        return f"{self.user.username} ↔ {self.email}"

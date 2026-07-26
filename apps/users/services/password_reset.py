"""Universal password reset — one flow for every role.

Deliberate security properties:
  * The response to a reset request never reveals whether an account exists.
  * Only a SHA-256 hash of the token is stored (see PasswordResetToken).
  * Tokens are single-use and time-limited.
  * Issuing a new token invalidates any outstanding ones for that user.
  * Completing a reset clears `is_first_login`, so the user is not immediately
    forced through the temporary-password change screen as well.
"""

from __future__ import annotations

import hashlib
import secrets

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from apps.users.models import PasswordResetToken, User


class PasswordResetError(Exception):
    """Raised when a reset token is missing, expired, already used, or invalid."""


def _hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _reset_link(raw_token: str) -> str:
    return f"{settings.FRONTEND_BASE_URL}/reset-password?token={raw_token}"


@transaction.atomic
def request_password_reset(*, email: str, ip: str | None = None) -> bool:
    """Issue a reset token and email it. Returns True if a mail was sent.

    Callers must NOT surface the return value to the user — always respond with
    the same "if an account exists, we've sent a link" message. The boolean is
    for logging and tests only.
    """
    email = (email or "").strip().lower()
    if not email:
        return False

    user = User.objects.filter(email__iexact=email, is_active=True).first()
    if not user:
        return False

    # Invalidate outstanding tokens so only the newest link works.
    PasswordResetToken.objects.filter(user=user, used_at__isnull=True).update(
        used_at=timezone.now()
    )

    raw_token = secrets.token_urlsafe(48)
    minutes = settings.PASSWORD_RESET_TIMEOUT_MINUTES
    PasswordResetToken.objects.create(
        user=user,
        token_hash=_hash(raw_token),
        expires_at=timezone.now() + timezone.timedelta(minutes=minutes),
        requested_ip=ip,
    )

    display_name = user.first_name or user.username
    send_mail(
        subject="Reset your MTAAS password",
        message=(
            f"Hello {display_name},\n\n"
            f"We received a request to reset the password for your MTAAS account "
            f"({user.username}).\n\n"
            f"Open this link to choose a new password:\n{_reset_link(raw_token)}\n\n"
            f"The link expires in {minutes} minutes and can only be used once.\n\n"
            f"If you did not request this, you can ignore this email — your "
            f"password will not change.\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return True


@transaction.atomic
def reset_password(*, raw_token: str, new_password: str) -> User:
    """Consume a reset token and set the new password. Raises PasswordResetError."""
    if not raw_token:
        raise PasswordResetError("Reset link is missing its token.")
    if len(new_password or "") < 8:
        raise PasswordResetError("Password must be at least 8 characters.")

    token = (
        PasswordResetToken.objects.select_for_update()
        .select_related("user")
        .filter(token_hash=_hash(raw_token))
        .first()
    )
    # Same message for "never existed" and "already consumed" — distinguishing
    # them would let someone probe which links were real.
    if not token or not token.is_usable:
        raise PasswordResetError("This reset link is invalid or has expired.")

    user = token.user
    user.set_password(new_password)
    # The reset itself proves control of the mailbox, so the temporary-password
    # prompt would be redundant noise on next sign-in.
    user.is_first_login = False
    user.save(update_fields=["password", "is_first_login"])

    token.used_at = timezone.now()
    token.save(update_fields=["used_at"])
    return user

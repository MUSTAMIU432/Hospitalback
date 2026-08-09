"""Universal password reset — one flow for every role.

Deliberate security properties:
  * The response to a reset request never reveals whether an account exists.
  * Only a SHA-256 hash of `email:code` is stored (see PasswordResetToken), so a
    leaked dump cannot be replayed and codes are scoped to one account.
  * Codes are single-use, time-limited, and attempt-limited.
  * Issuing a new code invalidates any outstanding ones for that user.
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

CODE_LENGTH = 6
MAX_ATTEMPTS = 6


class PasswordResetError(Exception):
    """Raised when a reset code is missing, wrong, expired, or already used."""


def _hash(email: str, code: str) -> str:
    """Scope the hash to the address: six digits alone would collide across users."""
    return hashlib.sha256(f"{email.strip().lower()}:{code.strip()}".encode("utf-8")).hexdigest()


def _new_code() -> str:
    return f"{secrets.randbelow(10 ** CODE_LENGTH):0{CODE_LENGTH}d}"


@transaction.atomic
def request_password_reset(*, email: str, ip: str | None = None) -> bool:
    """Issue a one-time code and email it. Returns True if a mail was sent.

    Callers must NOT surface the return value to the user — always respond with
    the same "if an account exists, we've sent a code" message. The boolean is
    for logging and tests only.
    """
    email = (email or "").strip().lower()
    if not email:
        return False

    user = User.objects.filter(email__iexact=email, is_active=True).first()
    if not user:
        return False

    # Invalidate outstanding codes so only the newest one works.
    PasswordResetToken.objects.filter(user=user, used_at__isnull=True).update(
        used_at=timezone.now()
    )

    code = _new_code()
    minutes = settings.PASSWORD_RESET_TIMEOUT_MINUTES
    PasswordResetToken.objects.create(
        user=user,
        token_hash=_hash(user.email, code),
        expires_at=timezone.now() + timezone.timedelta(minutes=minutes),
        requested_ip=ip,
    )

    display_name = user.first_name or user.username
    send_mail(
        subject=f"{code} is your MTAAS password reset code",
        message=(
            f"Hello {display_name},\n\n"
            f"We received a request to reset the password for your MTAAS account "
            f"({user.username}).\n\n"
            f"Your verification code is: {code}\n\n"
            f"Enter it on the password reset screen to choose a new password. The "
            f"code expires in {minutes} minutes and can only be used once.\n\n"
            f"If you did not request this, you can ignore this email — your "
            f"password will not change.\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return True


def _consume_lookup(email: str, code: str) -> PasswordResetToken:
    """Find the live token for this address+code, counting failed attempts.

    Attempts are counted against the account's newest outstanding token, so a
    brute-force run burns the code rather than getting unlimited guesses.
    """
    email = (email or "").strip().lower()
    code = (code or "").strip()
    if not email or not code:
        raise PasswordResetError("Enter the code we emailed you.")

    token = (
        PasswordResetToken.objects.select_for_update()
        .select_related("user")
        .filter(token_hash=_hash(email, code))
        .first()
    )
    if token is not None and token.is_usable:
        return token

    # Wrong or stale code: burn an attempt on the account's live token, if any.
    user = User.objects.filter(email__iexact=email, is_active=True).first()
    if user is not None:
        live = (
            PasswordResetToken.objects.select_for_update()
            .filter(user=user, used_at__isnull=True, expires_at__gt=timezone.now())
            .order_by("-created_at")
            .first()
        )
        if live is not None:
            live.attempts += 1
            if live.attempts >= MAX_ATTEMPTS:
                live.used_at = timezone.now()
                live.save(update_fields=["attempts", "used_at"])
                raise PasswordResetError(
                    "Too many incorrect codes. Request a new one to continue."
                )
            live.save(update_fields=["attempts"])

    # Same message whichever way it failed — distinguishing them would leak
    # whether the address has a pending reset.
    raise PasswordResetError("That code is incorrect or has expired.")


@transaction.atomic
def verify_reset_code(*, email: str, code: str) -> bool:
    """Check a code without consuming it, so the UI can gate the password step."""
    _consume_lookup(email, code)
    return True


@transaction.atomic
def reset_password(*, email: str, code: str, new_password: str) -> User:
    """Consume a reset code and set the new password. Raises PasswordResetError."""
    if len(new_password or "") < 8:
        raise PasswordResetError("Password must be at least 8 characters.")

    token = _consume_lookup(email, code)

    user = token.user
    user.set_password(new_password)
    # The code itself proves control of the mailbox, so the temporary-password
    # prompt would be redundant noise on next sign-in.
    user.is_first_login = False
    user.save(update_fields=["password", "is_first_login"])

    token.used_at = timezone.now()
    token.save(update_fields=["used_at"])
    return user

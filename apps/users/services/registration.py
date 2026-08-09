"""Student self-registration.

Two entry points create an account without an administrator: the signup form
(`register_student`) and an unrecognised Google sign-in (`provision_student_from_google`).
Both produce the *same* shape of record, so everything downstream — login,
tokens, the profile gate — is identical regardless of how the user arrived.

What a freshly self-registered account is NOT
---------------------------------------------
It has a `User` row and nothing else. `StudentProfile` carries the fields the
platform actually reasons about — registration number, programme, faculty, year
of study — and every one of them is required and unique-constrained. We cannot
invent them from a signup form that only asks for a name and an email, and a
half-populated profile row would be worse than none: `students` listings,
placement matching and application eligibility all read those fields.

So the profile is created later, by the user, through
`Mutation.completeStudentProfile`. Until then `User.profile_complete` is False
and the SPA holds them on the completion form. `role` is STUDENT from the
outset, which is what keeps this safe: a self-registered account can only ever
see the student workspace, never a reviewer or admin one.
"""

from __future__ import annotations

import re

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.users.models import User
from core.constants import UserModule, UserRole


class RegistrationError(Exception):
    """Raised when a self-registration request cannot be accepted."""


# Deliberately permissive: this is a sanity check, not an RFC 5322 parser. The
# authoritative check for a Google-sourced address is Google's own
# `email_verified` claim; for the signup form it is that the user can read mail
# there (enforced by password reset, not here).
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# User.username is max_length=50 and unique. Email addresses are the natural
# username for a self-registered student — they are unique, the user already
# knows theirs, and it keeps `authenticate(username=<what they typed>)` working
# with no changes to the login resolver.
_USERNAME_MAX = 50


def _normalise_email(email: str) -> str:
    email = (email or "").strip().lower()
    if not email:
        raise RegistrationError("Email address is required.")
    if not _EMAIL_RE.match(email):
        raise RegistrationError("Enter a valid email address.")
    if len(email) > _USERNAME_MAX:
        raise RegistrationError(
            f"Email address is too long — use one of {_USERNAME_MAX} characters or fewer."
        )
    return email


def _assert_email_free(email: str) -> None:
    """Reject an address already in use, by username or by email.

    Both columns are checked because admin-provisioned students have
    `username=<registration no>` with the address only in `email`, while
    self-registered ones have it in both.
    """
    taken = (
        User.objects.filter(email__iexact=email).exists()
        or User.objects.filter(username__iexact=email).exists()
    )
    if taken:
        raise RegistrationError(
            "An account already exists for this email address. "
            "Sign in instead, or use “Forgot password” if you cannot get in."
        )


def _clean_name(value: str, *, field: str) -> str:
    value = (value or "").strip()
    if not value:
        raise RegistrationError(f"{field} is required.")
    # first_name / last_name are max_length=150 on AbstractUser.
    return value[:150]


@transaction.atomic
def register_student(
    *,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
) -> User:
    """Create a student account from the public signup form.

    The password is run through Django's configured validators so the signup
    form cannot become a weaker door into the same platform than the admin
    provisioning path.
    """
    first_name = _clean_name(first_name, field="First name")
    last_name = _clean_name(last_name, field="Last name")
    email = _normalise_email(email)
    _assert_email_free(email)

    if not password:
        raise RegistrationError("Password is required.")
    try:
        validate_password(password)
    except DjangoValidationError as exc:
        raise RegistrationError(" ".join(exc.messages)) from exc

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=UserRole.STUDENT,
        module=UserModule.ATTACHMENT,
    )
    # They chose this password themselves — there is no administrator-set
    # temporary credential to nag them about. This also switches off the
    # first-name default-password fallback in student_credentials.
    user.is_first_login = False
    user.save(update_fields=["is_first_login"])
    return user


@transaction.atomic
def provision_student_from_google(
    *,
    google_sub: str,
    email: str,
    first_name: str,
    last_name: str,
) -> User:
    """Create a student account for a verified Google identity with no STUD match.

    Called only from `google_auth.resolve_user_for_google`, and only after the
    ID token's signature, audience, issuer, expiry and `email_verified` claim
    have all been checked — so the address is proven, unlike the signup form's.

    No password is set. `set_unusable_password()` means the account cannot be
    entered by guessing a password; the user signs in with Google, or claims a
    password of their own through the normal reset-by-email flow.
    """
    # Imported here rather than at module scope: models.GoogleIdentity imports
    # cleanly, but keeping the auth-service dependency one-directional avoids a
    # cycle if google_auth ever needs something from this module beyond this call.
    from django.utils import timezone

    from apps.users.models import GoogleIdentity

    email = _normalise_email(email)
    _assert_email_free(email)

    # Google's `given_name` / `family_name` are optional claims — a user with a
    # single-word display name supplies neither. Falling back to the local part
    # keeps first_name non-empty, which several UI labels assume.
    first_name = (first_name or "").strip() or email.split("@")[0]
    last_name = (last_name or "").strip()

    user = User.objects.create_user(
        username=email,
        email=email,
        password=None,
        first_name=first_name[:150],
        last_name=last_name[:150],
        role=UserRole.STUDENT,
        module=UserModule.ATTACHMENT,
    )
    user.set_unusable_password()
    user.is_first_login = False
    user.save(update_fields=["password", "is_first_login"])

    GoogleIdentity.objects.create(
        user=user,
        google_sub=google_sub,
        email=email,
        last_login_at=timezone.now(),
    )
    return user

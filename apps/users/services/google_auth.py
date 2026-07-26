"""Google Sign-In: verify an ID token and resolve it to a STUD user.

Flow: the SPA runs Google Identity Services, which hands the browser a signed
JWT ("ID token"). The SPA posts that token to `Mutation.loginWithGoogle`. This
module verifies it and returns the matching User; the mutation then issues our
normal access/refresh JWTs, so the rest of the platform is unchanged.

We deliberately do NOT trust anything the browser tells us about who the user
is — only claims inside a token whose signature verifies against Google's
public keys, and whose `aud` matches our own client ID.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from apps.users.models import GoogleIdentity, User

# Google mints ID tokens with one of these two issuers.
_VALID_ISSUERS = ("accounts.google.com", "https://accounts.google.com")


class GoogleAuthError(Exception):
    """Raised when a Google ID token cannot be trusted or matched to a user."""


@dataclass(frozen=True)
class GoogleProfile:
    sub: str
    email: str
    email_verified: bool
    first_name: str
    last_name: str


def verify_google_id_token(raw_token: str) -> GoogleProfile:
    """Verify signature, audience, issuer and expiry. Raises GoogleAuthError."""
    if not settings.GOOGLE_CLIENT_ID:
        raise GoogleAuthError("Google Sign-In is not configured on this server.")
    if not raw_token:
        raise GoogleAuthError("Missing Google credential.")

    try:
        # Fetches and caches Google's public keys, then checks signature, `aud`
        # against our client ID, and `exp`. Raises ValueError on any mismatch.
        claims = google_id_token.verify_oauth2_token(
            raw_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError as exc:
        raise GoogleAuthError(f"Invalid Google credential: {exc}") from exc

    if claims.get("iss") not in _VALID_ISSUERS:
        raise GoogleAuthError("Unrecognised token issuer.")

    email = (claims.get("email") or "").strip().lower()
    if not email:
        raise GoogleAuthError("Google account did not supply an email address.")

    # An unverified Google email proves nothing — anyone can attach an
    # arbitrary address to an account until Google confirms it. Refusing here
    # stops an attacker claiming a staff member's address.
    if not claims.get("email_verified", False):
        raise GoogleAuthError("This Google account's email address is not verified.")

    return GoogleProfile(
        sub=str(claims["sub"]),
        email=email,
        email_verified=True,
        first_name=(claims.get("given_name") or "").strip(),
        last_name=(claims.get("family_name") or "").strip(),
    )


@transaction.atomic
def resolve_user_for_google(profile: GoogleProfile) -> User:
    """Map a verified Google profile to an existing STUD user.

    Resolution order:
      1. A previously linked GoogleIdentity (stable, survives email changes).
      2. An existing user whose email matches — first-time link.

    Self-registration is intentionally NOT handled here. Accounts carry a role,
    module and capability set that decide what the user can see; minting one
    from a Google login would create a user with no meaningful authorisation.
    Until Section 3's registration flow exists, an unknown Google account is
    rejected rather than silently granted access.
    """
    identity = (
        GoogleIdentity.objects.select_related("user").filter(google_sub=profile.sub).first()
    )
    if identity:
        identity.last_login_at = timezone.now()
        # Keep the mirrored email current if they changed it at Google.
        if identity.email != profile.email:
            identity.email = profile.email
        identity.save(update_fields=["last_login_at", "email"])
        return identity.user

    user = User.objects.filter(email__iexact=profile.email).first()
    if not user:
        raise GoogleAuthError(
            "No STUD account is registered for this Google address. "
            "Contact your administrator to have an account created."
        )
    if not user.is_active:
        raise GoogleAuthError("This account is inactive.")

    GoogleIdentity.objects.create(
        user=user,
        google_sub=profile.sub,
        email=profile.email,
        last_login_at=timezone.now(),
    )
    # Signing in with a verified Google account clears the forced
    # password-change prompt: there is no temporary password left to rotate.
    if user.is_first_login:
        user.is_first_login = False
        user.save(update_fields=["is_first_login"])
    return user


def login_with_google(raw_token: str) -> User:
    return resolve_user_for_google(verify_google_id_token(raw_token))

from __future__ import annotations

import datetime as dt
from typing import Any

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model


def issue_access_token(user_id: str) -> str:
    now = dt.datetime.now(tz=dt.UTC)
    mins = int(getattr(settings, "JWT_ACCESS_EXPIRY_MINUTES", 60))
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "typ": "access",
        "iat": now,
        "exp": now + dt.timedelta(minutes=mins),
    }
    return jwt.encode(
        payload,
        settings.JWT_SIGNING_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def issue_refresh_token(user_id: str) -> str:
    now = dt.datetime.now(tz=dt.UTC)
    days = int(getattr(settings, "JWT_REFRESH_EXPIRY_DAYS", 14))
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "typ": "refresh",
        "iat": now,
        "exp": now + dt.timedelta(days=days),
    }
    return jwt.encode(
        payload,
        settings.JWT_SIGNING_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token,
            settings.JWT_SIGNING_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None


def get_user_id_from_token(token: str) -> str | None:
    data = decode_token(token)
    if not data:
        return None
    typ = data.get("typ")
    if typ is not None and typ != "access":
        return None
    sub = data.get("sub")
    return str(sub) if sub else None


def get_user_from_token(token: str):
    uid = get_user_id_from_token(token)
    if not uid:
        return None
    User = get_user_model()
    try:
        return User.objects.get(pk=uid, is_active=True)
    except User.DoesNotExist:
        return None


def get_user_from_refresh_token(token: str):
    data = decode_token(token)
    if not data or data.get("typ") != "refresh":
        return None
    sub = data.get("sub")
    if not sub:
        return None
    User = get_user_model()
    try:
        return User.objects.get(pk=str(sub), is_active=True)
    except User.DoesNotExist:
        return None

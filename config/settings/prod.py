from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403

DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"  # noqa: F405

# Tokens are HS256-signed with JWT_SIGNING_KEY. A blank or placeholder key means
# anyone can mint a token for any user, including a system administrator, so
# refuse to boot rather than serve a forgeable login. Failing the deploy is the
# cheap outcome here; the expensive one is nobody noticing.
if not DEBUG:
    _weak = {"", "dev-only-change-me", "change-me", "changeme"}
    _key = (JWT_SIGNING_KEY or "").strip()  # noqa: F405
    if _key in _weak or len(_key) < 32:
        raise ImproperlyConfigured(
            "JWT_SIGNING_KEY is missing, a placeholder, or shorter than 32 characters. "
            "Set a strong random JWT_SIGNING_KEY (and DJANGO_SECRET_KEY) in this "
            "environment — e.g. `python -c \"import secrets; print(secrets.token_urlsafe(64))\"`. "
            "Refusing to start: tokens signed with this key would be forgeable."
        )

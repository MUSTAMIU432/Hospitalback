import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.core.exceptions import ImproperlyConfigured
from dotenv import dotenv_values, load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = BASE_DIR / ".env"
# override=True: if the shell/IDE exports DATABASE_PASSWORD= (empty), still apply .env values.
# encoding=utf-8-sig: strip a UTF-8 BOM so the first key in .env is recognized.
load_dotenv(_ENV_FILE, override=True, encoding="utf-8-sig")


def _require_postgres_url(url: str) -> None:
    parsed = urlparse(url.strip())
    scheme = (parsed.scheme or "").lower()
    if scheme not in ("postgres", "postgresql"):
        raise ImproperlyConfigured(
            "STUD backend uses PostgreSQL only. Set DATABASE_URL to a URL whose "
            "scheme is postgresql:// (e.g. postgresql://user:pass@host:5432/KCHEKUNDU)."
        )
    db_name = (parsed.path or "").lstrip("/")
    if not db_name:
        raise ImproperlyConfigured(
            "DATABASE_URL must include the database name in the path "
            "(e.g. ...5432/KCHEKUNDU)."
        )


def _database_password(parsed_password: str | None) -> str:
    """
    Build the password sent to PostgreSQL (Django only passes it if non-empty).

    Order: ``DATABASE_PASSWORD`` / ``POSTGRES_PASSWORD`` in the environment
    (after ``load_dotenv``), same keys read literally from ``.env`` (no ``${}``
    interpolation), optional non-empty ``PGPASSWORD``, then the password
    embedded in ``DATABASE_URL`` (percent-decoded).

    Django's PostgreSQL backend does ``if settings_dict['PASSWORD']:`` before
    adding ``password`` to psycopg — so empty string == "no password supplied"
    at the server if auth requires a password.
    """
    for key in ("DATABASE_PASSWORD", "POSTGRES_PASSWORD"):
        v = os.environ.get(key)
        if v is not None and str(v).strip() != "":
            return str(v).strip()
    if _ENV_FILE.is_file():
        # interpolate=False avoids empty ${VAR} eating a literal password line.
        file_vals = dotenv_values(
            _ENV_FILE, encoding="utf-8-sig", interpolate=False
        )
        for key in ("DATABASE_PASSWORD", "POSTGRES_PASSWORD"):
            fv = file_vals.get(key)
            if fv is not None and str(fv).strip() != "":
                return str(fv).strip()
    pg = os.environ.get("PGPASSWORD")
    if pg is not None and str(pg).strip() != "":
        return str(pg).strip()
    if parsed_password:
        return unquote(parsed_password)
    return ""


def _database_from_url(url: str) -> dict:
    _require_postgres_url(url)
    parsed = urlparse(url.strip())
    path = (parsed.path or "").lstrip("/")
    password = _database_password(parsed.password)
    user = (os.environ.get("DATABASE_USER") or "").strip() or (parsed.username or "")
    host = (os.environ.get("DATABASE_HOST") or "").strip() or (parsed.hostname or "localhost")
    port = (os.environ.get("DATABASE_PORT") or "").strip() or str(parsed.port or 5432)
    name = (os.environ.get("DATABASE_NAME") or "").strip() or path
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": name,
        "USER": user,
        "PASSWORD": password,
        "HOST": host,
        "PORT": port,
        "CONN_MAX_AGE": int(os.environ.get("DATABASE_CONN_MAX_AGE", "0")),
        "OPTIONS": {
            "connect_timeout": int(os.environ.get("DATABASE_CONNECT_TIMEOUT", "10")),
        },
    }


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "strawberry.django",
    "apps.users",
    "apps.hospital_directory",
    "apps.employees",
    "apps.students",
    # Label stays "applications" for DB tables / migrations; see AppConfig.verbose_name in admin.
    "apps.applications.apps.ApplicationsConfig",
    "apps.notifications",
    "apps.imports",
    "apps.reports",
]

def _cors_origins() -> list[str]:
    raw = os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:8080,http://127.0.0.1:8080",
    )
    return [o.strip() for o in raw.split(",") if o.strip()]


CORS_ALLOWED_ORIGINS = _cors_origins()
CORS_ALLOW_CREDENTIALS = True

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "config.middleware.JWTAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

_DEFAULT_DATABASE_URL = "postgresql://postgres@127.0.0.1:5432/KCHEKUNDU"
DATABASES = {
    "default": _database_from_url(
        os.environ.get("DATABASE_URL", _DEFAULT_DATABASE_URL)
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

JWT_SIGNING_KEY = os.environ.get("JWT_SIGNING_KEY", SECRET_KEY)
JWT_ALGORITHM = "HS256"
# Short-lived access tokens (Authorization: Bearer …). Prefer minutes over the legacy hours setting.
JWT_ACCESS_EXPIRY_MINUTES = int(os.environ.get("JWT_ACCESS_EXPIRY_MINUTES", "60"))
# Long-lived refresh tokens returned by Mutation.login / Mutation.refreshToken (rotate on refresh).
JWT_REFRESH_EXPIRY_DAYS = int(os.environ.get("JWT_REFRESH_EXPIRY_DAYS", "14"))
# Deprecated: kept for backwards compatibility if code still reads it; access expiry uses JWT_ACCESS_EXPIRY_MINUTES.
JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))

# When true and DEFAULT_FROM_EMAIL / SMTP are configured, in-app notifications also send email.
STUD_EMAIL_NOTIFICATIONS = os.environ.get("STUD_EMAIL_NOTIFICATIONS", "0") == "1"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "webmaster@localhost")
EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)

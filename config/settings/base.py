import os
import socket
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

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


# libpq/psycopg connection keywords we accept from the DATABASE_URL query string
# (e.g. Render/Heroku append ?sslmode=require). Anything else is ignored so an
# unknown query param can't crash psycopg with an unexpected keyword.
_PASSTHROUGH_DB_PARAMS = frozenset({
    "sslmode", "sslrootcert", "sslcert", "sslkey", "target_session_attrs",
    "application_name", "options",
})


def _database_from_url(url: str) -> dict:
    _require_postgres_url(url)
    parsed = urlparse(url.strip())
    path = (parsed.path or "").lstrip("/")
    password = _database_password(parsed.password)
    user = (os.environ.get("DATABASE_USER") or "").strip() or (parsed.username or "")
    host = (os.environ.get("DATABASE_HOST") or "").strip() or (parsed.hostname or "localhost")
    port = (os.environ.get("DATABASE_PORT") or "").strip() or str(parsed.port or 5432)
    name = (os.environ.get("DATABASE_NAME") or "").strip() or path

    options = {"connect_timeout": int(os.environ.get("DATABASE_CONNECT_TIMEOUT", "10"))}
    # Honour libpq params from the URL query (?sslmode=require etc.) — without this
    # a managed host that mandates SSL would be reached with the driver's default.
    for key, values in parse_qs(parsed.query).items():
        if key in _PASSTHROUGH_DB_PARAMS and values:
            options[key] = values[0]
    # Explicit override always wins over whatever the URL carried.
    sslmode_env = (os.environ.get("DATABASE_SSLMODE") or "").strip()
    if sslmode_env:
        options["sslmode"] = sslmode_env

    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": name,
        "USER": user,
        "PASSWORD": password,
        "HOST": host,
        "PORT": port,
        "CONN_MAX_AGE": int(os.environ.get("DATABASE_CONN_MAX_AGE", "0")),
        "OPTIONS": options,
    }


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"


def _local_ipv4s() -> list[str]:
    """This machine's own LAN addresses.

    Phones reach the API at http://<this machine>:8000, and that address changes
    with every network and DHCP lease. Pinning it in .env means the API starts
    answering 400 DisallowedHost the moment the lease changes — the request never
    reaches a view, so the symptom on the phone is a working app that can never
    connect. Asking the OS removes the pin.

    Connecting a UDP socket sends no packets; it only makes the kernel choose the
    interface it would route through.
    """
    found: list[str] = []
    for target in ("8.8.8.8:80", "224.0.0.1:80"):
        host, port = target.split(":")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect((host, int(port)))
            ip = sock.getsockname()[0]
            if ip and not ip.startswith("127.") and ip not in found:
                found.append(ip)
        except OSError:
            pass
        finally:
            sock.close()
    return found


ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]
# Always trust our own addresses, whatever .env happens to say. Without this a
# stale DJANGO_ALLOWED_HOSTS silently breaks every phone on the network.
for _ip in _local_ipv4s():
    if _ip not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_ip)

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
    "apps.chatbot",
]

def _cors_origins() -> list[str]:
    raw = os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:8080,http://127.0.0.1:8080,"
        # Mobile APK WebView origins. Tauri's Android WebView serves the bundled
        # SPA from http://tauri.localhost; Capacitor with androidScheme:"http"
        # uses plain http://localhost.
        "http://localhost,https://localhost,capacitor://localhost,"
        "http://tauri.localhost,https://tauri.localhost",
    )
    return [o.strip() for o in raw.split(",") if o.strip()]


CORS_ALLOWED_ORIGINS = _cors_origins()
# A phone browsing the Vite dev server does so from http://<lan-ip>:5173, which
# a pinned .env list will not contain after the address changes.
for _ip in _local_ipv4s():
    for _port in ("3000", "5173", "5174", "8000", "8080"):
        _origin = f"http://{_ip}:{_port}"
        if _origin not in CORS_ALLOWED_ORIGINS:
            CORS_ALLOWED_ORIGINS.append(_origin)
CORS_ALLOW_CREDENTIALS = True
# Allow any localhost:PORT and capacitor origins (covers WebView quirks in dev).
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://localhost(:\d+)?$",
    r"^https://localhost(:\d+)?$",
    r"^https?://tauri\.localhost(:\d+)?$",
    r"^http://127\.0\.0\.1(:\d+)?$",
    r"^capacitor://localhost$",
]

if DEBUG:
    # Development on a LAN: any private-range origin may call the API. Scoped to
    # DEBUG so a production deployment keeps the explicit allow-list above.
    CORS_ALLOWED_ORIGIN_REGEXES += [
        r"^http://192\.168\.\d{1,3}\.\d{1,3}(:\d+)?$",
        r"^http://10\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$",
        r"^http://172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}(:\d+)?$",
    ]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Whitenoise serves static files (Django admin CSS, etc.) in production.
    # Must come right after SecurityMiddleware and before everything else.
    "whitenoise.middleware.WhiteNoiseMiddleware",
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

# Whitenoise: compress + hash static filenames so they cache well and serve fast.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

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

# ── Google Sign-In (OAuth 2.0) ───────────────────────────────────────────────
# Client ID/secret come from Google Cloud Console → Credentials → OAuth client ID
# (type: Web application). The ID is public and also ships to the SPA as
# VITE_GOOGLE_CLIENT_ID; the secret must stay server-side.
#
# Values are stripped of stray whitespace and a trailing ";" — pasting from the
# console often carries one, and it silently breaks token verification with
# `invalid_client`, which is very hard to diagnose from Google's error alone.
def _clean_env(name: str) -> str:
    return os.environ.get(name, "").strip().rstrip(";").strip()


GOOGLE_CLIENT_ID = _clean_env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = _clean_env("GOOGLE_CLIENT_SECRET")
GOOGLE_SIGNIN_ENABLED = bool(GOOGLE_CLIENT_ID)

# How long a password-reset link stays valid.
PASSWORD_RESET_TIMEOUT_MINUTES = int(os.environ.get("PASSWORD_RESET_TIMEOUT_MINUTES", "30"))
# Base URL of the SPA — used to build the reset link inside the email.
FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")

# ── Email / SMTP ─────────────────────────────────────────────────────────────
# Set STUD_EMAIL_NOTIFICATIONS=1 in .env to enable email delivery.
# Configure the SMTP_ vars below (or use Gmail with an App Password).
STUD_EMAIL_NOTIFICATIONS = os.environ.get("STUD_EMAIL_NOTIFICATIONS", "0") == "1"

EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST          = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT          = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS       = os.environ.get("EMAIL_USE_TLS", "1") == "1"
EMAIL_USE_SSL       = os.environ.get("EMAIL_USE_SSL", "0") == "1"
EMAIL_HOST_USER     = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL  = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER or "webmaster@localhost",
)
SERVER_EMAIL        = DEFAULT_FROM_EMAIL

# ── AI / workflow chat ───────────────────────────────────────────────────────
# Groq is the default provider (OpenAI-compatible endpoint): set GROQ_API_KEY in
# .env. Any other compatible provider works by overriding the URL/model vars.
# The key stays server-side — the SPA only ever calls our own GraphQL mutation.
GROQ_API_KEY = _clean_env("GROQ_API_KEY")
CHATBOT_API_KEY = GROQ_API_KEY or _clean_env("CHATBOTAPIKEY") or _clean_env("CHATBOT_API_KEY")
_chatbot_on_groq = bool(GROQ_API_KEY)
CHATBOT_PROVIDER = (
    os.environ.get("CHATBOT_PROVIDER", "Groq" if _chatbot_on_groq else "OpenAI").strip()
    or "Groq"
)
CHATBOT_API_BASE_URL = os.environ.get(
    "CHATBOT_API_BASE_URL",
    "https://api.groq.com/openai" if _chatbot_on_groq else "https://api.openai.com",
).strip().rstrip("/")
CHATBOT_API_PATH = os.environ.get("CHATBOT_API_PATH", "/v1/chat/completions").strip() or "/v1/chat/completions"
CHATBOT_API_URL = f"{CHATBOT_API_BASE_URL}{CHATBOT_API_PATH if CHATBOT_API_PATH.startswith('/') else '/' + CHATBOT_API_PATH}"
_default_model = "llama-3.3-70b-versatile" if _chatbot_on_groq else "gpt-4o-mini"
CHATBOT_MODEL = os.environ.get("CHATBOT_MODEL", _default_model).strip() or _default_model
CHATBOT_REFERER = os.environ.get("CHATBOT_REFERER", FRONTEND_BASE_URL).strip()
CHATBOT_TITLE = os.environ.get("CHATBOT_TITLE", "STUD Workflow Assistant").strip()
CHATBOT_TEMPERATURE = float(os.environ.get("CHATBOT_TEMPERATURE", "0.3"))
CHATBOT_MAX_TOKENS = int(os.environ.get("CHATBOT_MAX_TOKENS", "500"))

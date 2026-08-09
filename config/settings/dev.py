"""Local development: same database stack as production (PostgreSQL only)."""

from .base import *  # noqa: F401,F403

DEBUG = True

# The Android emulator reaches the host machine through the NAT alias 10.0.2.2,
# which is not one of our own interface addresses, so base.py's auto-trust loop
# cannot discover it. The frontend probes it deliberately during backend
# discovery (src/lib/config/environment.ts), so allow it here — dev only.
if "10.0.2.2" not in ALLOWED_HOSTS:  # noqa: F405
    ALLOWED_HOSTS.append("10.0.2.2")  # noqa: F405

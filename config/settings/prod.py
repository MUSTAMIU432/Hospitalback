from .base import *  # noqa: F401,F403

DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"  # noqa: F405

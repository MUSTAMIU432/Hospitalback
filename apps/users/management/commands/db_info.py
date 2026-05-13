"""Show which PostgreSQL database Django is configured to use."""

import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from dotenv import dotenv_values


class Command(BaseCommand):
    help = (
        "Print active DATABASES['default'] (PostgreSQL engine, name, host). "
        "Use after editing project-root `.env`."
    )

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        env_file = base_dir / ".env"

        db = settings.DATABASES["default"]
        engine = db.get("ENGINE", "")
        name = db.get("NAME", "")
        self.stdout.write(self.style.NOTICE("Active default database:"))
        self.stdout.write(f"  ENGINE: {engine}")
        self.stdout.write(f"  NAME:   {name}")
        self.stdout.write(f"  .env file: {env_file}  exists={env_file.is_file()}")

        def _status(key: str) -> str:
            if key not in os.environ:
                return "missing"
            v = os.environ[key]
            if str(v).strip() == "":
                return "empty (Django will not send a password)"
            return f"set, len={len(str(v))}"

        self.stdout.write(f"  DATABASE_PASSWORD (os.environ): {_status('DATABASE_PASSWORD')}")
        self.stdout.write(f"  POSTGRES_PASSWORD (os.environ): {_status('POSTGRES_PASSWORD')}")
        self.stdout.write(f"  PGPASSWORD (os.environ): {_status('PGPASSWORD')}")

        if env_file.is_file():
            raw = dotenv_values(env_file, encoding="utf-8-sig", interpolate=False)
            for key in ("DATABASE_PASSWORD", "POSTGRES_PASSWORD"):
                fv = raw.get(key)
                if fv is None:
                    self.stdout.write(f"  {key} (raw .env file): absent")
                elif str(fv).strip() == "":
                    self.stdout.write(
                        f"  {key} (raw .env file): empty line — remove it or set a value"
                    )
                else:
                    self.stdout.write(
                        f"  {key} (raw .env file): present, len={len(str(fv))}"
                    )

        if "postgresql" not in engine:
            self.stdout.write(
                self.style.ERROR(
                    "Expected PostgreSQL. Check DATABASE_URL in project-root `.env`."
                )
            )
            return
        self.stdout.write(f"  HOST:   {db.get('HOST')}")
        self.stdout.write(f"  PORT:   {db.get('PORT')}")
        self.stdout.write(f"  USER:   {db.get('USER') or '(empty)'}")
        pw_set = bool(db.get("PASSWORD"))
        self.stdout.write(f"  PASSWORD (resolved for Django/psycopg): {'set' if pw_set else 'empty'}")
        if not pw_set:
            self.stdout.write(
                self.style.WARNING(
                    "Django's PostgreSQL backend only sends a password if this field is "
                    "non-empty (see django.db.backends.postgresql.base.get_connection_params). "
                    "Use DATABASE_PASSWORD or POSTGRES_PASSWORD in .env, or embed the password "
                    "in DATABASE_URL (encode special chars). Remove any empty DATABASE_PASSWORD= line."
                )
            )

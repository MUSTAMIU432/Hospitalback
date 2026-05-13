"""
Insert practice rows into PostgreSQL tables (users, hospital_staff, student_profiles)
via the ORM — same outcome as INSERT … executed against those tables.

Idempotent on usernames / staff_number / registration_no.

Run after migrations and (optionally) seed_hospital_directory:

  python manage.py seed_hospital_directory
  python manage.py seed_practice_dataset --password='your-secret-here'

Or set ``STUD_PRACTICE_SEED_PASSWORD`` in the environment instead of ``--password``.

**Easy local sign-in (optional):** student **usernames** are ``studprac_<firstnamelower>`` (e.g. ``studprac_mary``)
so they do not collide with real accounts named ``mary`` / ``james``. **Password** is still the stored
``first_name`` (e.g. ``Mary``, case-sensitive). Hospital staff still use ``H001``…``H006``; initial password is each
user’s ``first_name`` (e.g. ``Practice Staff 1``). All such users get ``is_first_login=True`` so STUDFRONT sends
them to change password after first login. Enable with ``--easy-login`` or ``STUD_PRACTICE_EASY_LOGIN=1``.

Re-run: profile fields update each time. With ``--password`` mode, passwords are set only when a
practice user has no usable password yet, or when ``--reset-password`` is passed (both require the secret above).
With ``--easy-login``, passwords follow the rule above whenever a password must be written.
"""

from __future__ import annotations

import os
import re
from datetime import date

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.employees.models import HospitalStaff
from apps.hospital_directory.models import Department, Designation, WorkingSite
from apps.students.models import StudentProfile
from apps.users.services import provisioning
from core.constants import Gender, UserModule, UserRole

User = get_user_model()

STAFF_COUNT = 6
STUDENT_COUNT = 6

# First names for easy-login students; login username = studprac_<slug(first name)> (avoids clashes with real users).
STUDENT_FIRST_NAMES = ["Mary", "James", "Sara", "Peter", "Amina", "John"]

EASY_STUDENT_USERNAME_PREFIX = "studprac_"


def practice_student_username(first_name: str) -> str:
    """Reserved practice-login usernames — unlikely to match production human-chosen logins."""
    slug = re.sub(r"[^a-z0-9]+", "", (first_name or "").strip().lower())
    if not slug:
        slug = "student"
    return f"{EASY_STUDENT_USERNAME_PREFIX}{slug}"


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _easy_login_password(user: User) -> str:
    """Initial password for practice users: stored first_name, else username (set_password bypasses min length)."""
    return (user.first_name or "").strip() or user.get_username()


class Command(BaseCommand):
    help = (
        "Write practice hospital staff (H001–H006) and students (S001–S006) into the database "
        "(users + hospital_staff / student_profiles tables)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="",
            help=(
                "Password for practice users when creating or resetting their login. "
                "May be omitted if env STUD_PRACTICE_SEED_PASSWORD is set. "
                "Required whenever a password must be written (first seed or --reset-password)."
            ),
        )
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help=(
                "Set password for all seeded practice accounts. With --easy-login, no shared secret is needed; "
                "otherwise requires --password or STUD_PRACTICE_SEED_PASSWORD."
            ),
        )
        parser.add_argument(
            "--skip-directory",
            action="store_true",
            help="Do not run seed_hospital_directory first (fail if no departments).",
        )
        parser.add_argument(
            "--easy-login",
            action="store_true",
            help=(
                "Development sign-in: student usernames are studprac_<firstname> (e.g. studprac_mary) to avoid "
                "collisions with existing users; password is still first_name (e.g. Mary). "
                "Sets is_first_login=True. Does not require --password. Same as env STUD_PRACTICE_EASY_LOGIN=1."
            ),
        )

    def handle(self, *args, **options):
        reset_pw = options["reset_password"]
        easy_login = bool(options["easy_login"]) or _truthy_env("STUD_PRACTICE_EASY_LOGIN")
        pw = (options.get("password") or "").strip() or (os.environ.get("STUD_PRACTICE_SEED_PASSWORD") or "").strip()
        if easy_login and pw:
            self.stdout.write(
                self.style.WARNING(
                    "Ignoring --password / STUD_PRACTICE_SEED_PASSWORD because --easy-login is active."
                )
            )
            pw = ""
        if reset_pw and not pw and not easy_login:
            raise CommandError(
                "When using --reset-password, pass --password='…' or export STUD_PRACTICE_SEED_PASSWORD. "
                "There is no built-in default password (unless you use --easy-login)."
            )
        if pw and len(pw) < 8 and not easy_login:
            raise CommandError("Password must be at least 8 characters (same minimum as change-password).")

        if not options["skip_directory"]:
            call_command("seed_hospital_directory")

        dept = Department.objects.order_by("sort_order", "name").first()
        des = Designation.objects.order_by("sort_order", "name").first()
        site = WorkingSite.objects.order_by("sort_order", "name").first()
        if not dept or not des or not site:
            self.stderr.write(
                "No department/designation/working_site found. "
                "Run: python manage.py seed_hospital_directory"
            )
            return

        any_password_set = False

        def ensure_password(user, label: str) -> None:
            nonlocal any_password_set
            if easy_login:
                if not (reset_pw or not user.has_usable_password()):
                    return
                raw = _easy_login_password(user)
                if not raw:
                    raise CommandError(f"Practice user {label} has empty first_name and username; cannot set password.")
                user.set_password(raw)
                user.is_first_login = True
                any_password_set = True
                return
            if not (reset_pw or not user.has_usable_password()):
                return
            if not pw:
                raise CommandError(
                    f"Practice user {label} needs a password. Pass --password='…' or export "
                    "STUD_PRACTICE_SEED_PASSWORD (no default credentials in the codebase)."
                )
            user.set_password(pw)
            any_password_set = True

        with transaction.atomic():
            hod_user, _ = User.objects.get_or_create(
                username="hod_practice",
                defaults={
                    "email": "hod_practice@practice.local",
                    "first_name": "Practice HOD",
                    "role": UserRole.HOD,
                    "module": UserModule.FURTHER_STUDIES,
                    "is_first_login": False,
                },
            )
            hod_user.role = UserRole.HOD
            hod_user.module = UserModule.FURTHER_STUDIES
            hod_user.is_first_login = True if easy_login else False
            hod_user.is_active = True
            ensure_password(hod_user, "hod_practice")
            hod_user.save()

            for i in range(1, STAFF_COUNT + 1):
                sid = f"H{i:03d}"
                user, _ = User.objects.get_or_create(
                    username=sid,
                    defaults={
                        "email": f"{sid.lower()}@practice.local",
                        "first_name": f"Practice Staff {i}",
                        "role": UserRole.HOSPITAL_STAFF,
                        "module": UserModule.FURTHER_STUDIES,
                        "is_first_login": False,
                    },
                )
                user.email = user.email or f"{sid.lower()}@practice.local"
                user.first_name = f"Practice Staff {i}"
                user.role = UserRole.HOSPITAL_STAFF
                user.module = UserModule.FURTHER_STUDIES
                user.is_active = True
                user.is_first_login = True if easy_login else False
                ensure_password(user, sid)
                user.save()

                national = f"PRAC-NIDA-{sid}-1990-01-01"
                profile, created = HospitalStaff.objects.update_or_create(
                    user=user,
                    defaults={
                        "staff_number": sid,
                        "full_name": f"Practice Hospital Staff {i}",
                        "department": dept,
                        "designation": des,
                        "working_site": site,
                        "phone": f"+255700{i:06d}",
                        "national_id": national,
                        "date_employed": date(2020, 1, min(i, 28)),
                        "staff_role": provisioning.default_staff_role(),
                        "hod": hod_user if i <= 4 else None,
                        "capabilities": ["hr_field_requests"] if i == 1 else [],
                    },
                )
                profile.full_clean()
                profile.save()
                verb = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(f"{verb} hospital_staff + user: {sid}"))

            programmes = (
                "BSc Nursing",
                "MBBS",
                "BSc Midwifery",
                "BSc Public Health",
                "BSc Laboratory Sciences",
                "BSc Physiotherapy",
            )
            for i in range(1, STUDENT_COUNT + 1):
                reg = f"S{i:03d}"
                if easy_login:
                    fname = STUDENT_FIRST_NAMES[i - 1]
                    login_uname = practice_student_username(fname)
                else:
                    login_uname, fname = reg, f"Practice Student {i}"

                user, _ = User.objects.get_or_create(
                    username=login_uname,
                    defaults={
                        "email": f"{login_uname}@practice.local",
                        "first_name": fname,
                        "role": UserRole.STUDENT,
                        "module": UserModule.ATTACHMENT,
                        "is_first_login": False,
                    },
                )
                user.email = user.email or f"{login_uname}@practice.local"
                user.first_name = fname
                user.role = UserRole.STUDENT
                user.module = UserModule.ATTACHMENT
                user.is_active = True
                user.is_first_login = True if easy_login else False
                ensure_password(user, login_uname)
                user.save()

                dob = f"{i:02d}011998"  # DDMMYYYY
                # Key on registration_no (unique): easy-login moves the row from legacy user S001 → studprac_mary.
                profile, created = StudentProfile.objects.update_or_create(
                    registration_no=reg,
                    defaults={
                        "user": user,
                        "full_name": f"{fname} ({reg})",
                        "programme": programmes[i - 1],
                        "faculty": "Faculty of Health Sciences",
                        "year_of_study": ((i - 1) % 6) + 1,
                        "phone": f"+255710{i:06d}",
                        "contact_email": "",
                        "gender": Gender.FEMALE if i % 2 == 0 else Gender.MALE,
                        "dob": dob,
                        "university": "Zanzibar University",
                        "hospital_department": dept,
                        "dashboard_notes": "Seeded for login / UI practice.",
                        "supervisor": None,
                    },
                )
                profile.full_clean()
                profile.save()
                if easy_login:
                    n_legacy, _ = User.objects.filter(username=reg, role=UserRole.STUDENT).exclude(pk=user.pk).delete()
                    if n_legacy:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Replaced legacy student login {reg} with {login_uname} (same profile reg {reg})."
                            )
                        )
                verb = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(f"{verb} student_profiles + user: {login_uname} (reg {reg})"))

        self.stdout.write("")
        if easy_login:
            self.stdout.write(
                self.style.SUCCESS(
                    "Easy-login practice accounts (password = each user’s first_name, case-sensitive; "
                    "is_first_login=True → change password in STUDFRONT after first sign-in):"
                )
            )
            self.stdout.write("  Students — username studprac_<first name lower> / password (first name):")
            for fn in STUDENT_FIRST_NAMES:
                un = practice_student_username(fn)
                self.stdout.write(f"    {un} / {fn}")
            self.stdout.write("  Hospital staff: H001 … H006 — password = first name field, e.g. Practice Staff 1")
            self.stdout.write("  HOD reviewer: hod_practice — password = first name field Practice HOD")
            if any_password_set:
                self.stdout.write(self.style.WARNING("Passwords were (re)written using the easy-login rule above."))
            self.stdout.write("")
            self.stdout.write(
                "Re-apply easy-login passwords on existing rows: "
                "python manage.py seed_practice_dataset --easy-login --reset-password"
            )
        else:
            self.stdout.write(self.style.SUCCESS("Practice usernames (sign in with username + your chosen secret):"))
            self.stdout.write("  Hospital staff: H001 … H006 (H001 has HR capability)")
            self.stdout.write("  Students: S001 … S006")
            self.stdout.write("  HOD reviewer: hod_practice")
            if any_password_set:
                self.stdout.write(
                    self.style.WARNING(
                        "Passwords were set from --password / STUD_PRACTICE_SEED_PASSWORD (value not printed)."
                    )
                )
            self.stdout.write("")
            self.stdout.write(
                "Reset all practice passwords later: "
                "python manage.py seed_practice_dataset --reset-password --password='…'"
            )
            self.stdout.write(
                "Or use easy-login for local dev: "
                "python manage.py seed_practice_dataset --easy-login  (or STUD_PRACTICE_EASY_LOGIN=1)"
            )

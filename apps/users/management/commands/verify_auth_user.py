"""Show whether a username exists and can sign in to GraphQL (active, flags). Does not print the password."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Inspect a user row for login issues (exact username, is_active, superuser/role)."

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            nargs="?",
            default=None,
            help="Username to inspect. Omit to list all superusers.",
        )

    def handle(self, *args, **options):
        username = options["username"]
        if not username:
            qs = User.objects.filter(is_superuser=True).order_by("username")
            if not qs.exists():
                self.stdout.write(self.style.WARNING("No superusers in this database."))
                self.stdout.write("Create one: .venv/bin/python manage.py createsuperuser")
                return
            self.stdout.write("Superusers (sign in with this exact username, case-sensitive):")
            for u in qs:
                self._line(u)
            return

        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"No user with username {username!r} in this database."),
            )
            self.stdout.write("Typo? Spaces? Run without arguments to list superusers.")
            similar = User.objects.filter(username__icontains=username.strip()[:20])[:10]
            if similar.exists():
                self.stdout.write("Similar usernames:")
                for row in similar:
                    self.stdout.write(f"  - {row.username!r}")
            return

        self._line(u)
        if not u.is_active:
            self.stdout.write(
                self.style.ERROR("is_active is False — login will return Invalid credentials."),
            )
            self.stdout.write("Fix: Django shell, then set is_active=True for that user.")
        self.stdout.write("")
        self.stdout.write("Reset password (interactive):")
        self.stdout.write(f"  .venv/bin/python manage.py changepassword {username}")

    def _line(self, u: User) -> None:
        self.stdout.write(
            f"  {u.username!r}  active={u.is_active}  superuser={u.is_superuser}  "
            f"role={u.role!r}  module={u.module!r}  first_login={u.is_first_login}",
        )

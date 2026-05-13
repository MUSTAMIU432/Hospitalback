"""Remove old demo accounts (demo, demo_*). Does not remove practice seed users (H001, S001, …)."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

LEGACY_USERNAMES = (
    "demo",
    "demo_hospital_staff",
    "demo_student",
    "demo_reviewer",
    "demo_hospital_admin",
    "demo_univ_admin",
    "demo_employee",  # pre-rename hospital staff demo
)


class Command(BaseCommand):
    help = "Delete legacy demo users from the database (usernames: demo, demo_*)."

    def handle(self, *args, **options):
        qs = User.objects.filter(username__in=LEGACY_USERNAMES)
        n = qs.count()
        if n == 0:
            self.stdout.write("No legacy demo users found.")
            return
        _, deleted = qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Removed {n} legacy demo user(s). Delete summary: {deleted}"))

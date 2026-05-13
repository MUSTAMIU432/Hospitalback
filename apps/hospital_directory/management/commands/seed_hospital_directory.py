"""Create sample departments, designations, and working sites for local dev."""

from django.core.management.base import BaseCommand

from apps.hospital_directory.models import Department, Designation, WorkingSite


class Command(BaseCommand):
    help = "Idempotently seed hospital directory rows for dropdowns and employee FKs."

    def handle(self, *args, **options):
        created = 0
        depts = (
            ("Nursing Services", "NURS"),
            ("Medical Services", "MED"),
            ("Human Resources", "HR"),
        )
        for i, (name, code) in enumerate(depts):
            _, was_created = Department.objects.get_or_create(
                name=name,
                defaults={"code": code, "sort_order": i},
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created Department: {name}"))

        titles = ("Staff Nurse", "Medical Officer", "Administrator")
        for i, name in enumerate(titles):
            _, was_created = Designation.objects.get_or_create(
                name=name,
                defaults={"sort_order": i},
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created Designation: {name}"))

        sites = ("Main Hospital Campus", "Regional Clinic")
        for i, name in enumerate(sites):
            _, was_created = WorkingSite.objects.get_or_create(
                name=name,
                defaults={"sort_order": i},
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created WorkingSite: {name}"))

        if created == 0:
            self.stdout.write("Directory already populated (no new rows).")

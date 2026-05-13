# Generated manually — default rows for document kinds and sponsorship types.

from django.db import migrations


def forwards(apps, schema_editor):
    SponsorshipType = apps.get_model("hospital_directory", "SponsorshipType")
    ApplicationDocumentKind = apps.get_model("hospital_directory", "ApplicationDocumentKind")
    for i, name in enumerate(
        (
            "Government scholarship",
            "Self-sponsored",
            "Hospital sponsorship",
            "NGO / donor funded",
        )
    ):
        SponsorshipType.objects.get_or_create(name=name, defaults={"sort_order": i, "is_active": True})
    kinds = (
        ("supporting_letter", "Supporting letter", 0),
        ("id_copy", "ID copy", 1),
        ("cv", "CV / resume", 2),
        ("academic", "Academic record", 3),
        ("admission_letter", "University admission letter", 4),
        ("other", "Other", 99),
    )
    for code, label, so in kinds:
        ApplicationDocumentKind.objects.get_or_create(
            code=code, defaults={"label": label, "sort_order": so, "is_active": True}
        )


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("hospital_directory", "0002_registry_and_university_extensions"),
    ]

    operations = [migrations.RunPython(forwards, backwards)]

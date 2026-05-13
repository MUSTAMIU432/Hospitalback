from django.db import migrations


def forwards(apps, schema_editor):
    Application = apps.get_model("applications", "Application")
    Application.objects.filter(
        app_type="attachment",
        current_stage="management",
    ).exclude(status__in=("approved", "rejected")).update(current_stage="hr")


def backwards(apps, schema_editor):
    Application = apps.get_model("applications", "Application")
    Application.objects.filter(
        app_type="attachment",
        current_stage="hr",
    ).exclude(status__in=("approved", "rejected")).update(current_stage="management")


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0005_attachment_hr_placement_fields"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]

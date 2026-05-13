# Rename import batch type value employee → hospital_staff.

from django.db import migrations, models


def forwards_batch_type(apps, schema_editor):
    ImportBatch = apps.get_model("imports", "ImportBatch")
    ImportBatch.objects.filter(batch_type="employee").update(batch_type="hospital_staff")


def backwards_noop(apps, schema_editor):
    """Schema-only reverse; do not rewrite batch_type values."""


class Migration(migrations.Migration):

    dependencies = [
        ("imports", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(forwards_batch_type, backwards_noop),
        migrations.AlterField(
            model_name="importbatch",
            name="batch_type",
            field=models.CharField(
                choices=[
                    ("hospital_staff", "Hospital staff"),
                    ("student", "Student"),
                ],
                max_length=20,
            ),
        ),
    ]

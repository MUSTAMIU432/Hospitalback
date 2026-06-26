import uuid

import django.core.validators
from django.db import migrations, models


def backfill_sections(apps, schema_editor):
    """Create one CapabilitySection per distinct module on existing capabilities."""
    StaffCapability = apps.get_model("employees", "StaffCapability")
    CapabilitySection = apps.get_model("employees", "CapabilitySection")

    modules = (
        StaffCapability.objects.values_list("module", flat=True).distinct()
    )
    for order, module in enumerate(sorted({m for m in modules if m})):
        label = module.replace("_", " ").title()
        CapabilitySection.objects.get_or_create(
            key=module,
            defaults={"label": label, "sort_order": order, "is_active": True},
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0008_departmenthodassignment"),
    ]

    operations = [
        migrations.CreateModel(
            name="CapabilitySection",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "key",
                    models.CharField(
                        max_length=80,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[a-z0-9_]+$", "Use a lowercase key, e.g. field_management."
                            )
                        ],
                    ),
                ),
                ("label", models.CharField(max_length=180)),
                ("description", models.TextField(blank=True, default="")),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                "db_table": "capability_sections",
                "ordering": ["sort_order", "label"],
            },
        ),
        migrations.RunPython(backfill_sections, noop),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0005_rename_employee_number_to_staff_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="hospitalstaff",
            name="capabilities",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text=(
                    "Capability codes granted by hospital admin (e.g. hr_field_requests). "
                    "Role remains hospital_staff."
                ),
            ),
        ),
    ]

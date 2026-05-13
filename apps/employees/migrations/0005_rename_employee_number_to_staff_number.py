from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0004_hospital_staff_and_roles"),
    ]

    operations = [
        migrations.RenameField(
            model_name="hospitalstaff",
            old_name="employee_number",
            new_name="staff_number",
        ),
    ]

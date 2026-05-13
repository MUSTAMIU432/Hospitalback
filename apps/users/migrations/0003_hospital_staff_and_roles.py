# Remove legacy employee_admin role value in favour of hospital_admin.

from django.db import migrations, models


def forwards_map_employee_admin(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(role="employee_admin").update(role="hospital_admin")


def backwards_noop(apps, schema_editor):
    """Do not map hospital_admin → employee_admin (lossy); reverse is schema-only."""


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_user_role"),
    ]

    operations = [
        migrations.RunPython(forwards_map_employee_admin, backwards_noop),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("employee", "Employee"),
                    ("student", "Student"),
                    ("hod", "Head of Department"),
                    ("asst_director", "Assistant Director"),
                    ("management", "Management"),
                    ("hospital_admin", "Hospital Admin"),
                    ("univ_admin", "University Admin"),
                    ("sysadmin", "System Admin"),
                ],
                default="employee",
                max_length=30,
            ),
        ),
    ]

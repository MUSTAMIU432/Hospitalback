# Map legacy applicant role `employee` → `hospital_staff` and tighten choices.

from django.db import migrations, models


def forwards_role(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(role="employee").update(role="hospital_staff")


def backwards_role(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(role="hospital_staff").update(role="employee")


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_hospital_staff_and_roles"),
    ]

    operations = [
        migrations.RunPython(forwards_role, backwards_role),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("hospital_staff", "Hospital staff"),
                    ("student", "Student"),
                    ("hod", "Head of Department"),
                    ("asst_director", "Assistant Director"),
                    ("management", "Management"),
                    ("hospital_admin", "Hospital Admin"),
                    ("univ_admin", "University Admin"),
                    ("sysadmin", "System Admin"),
                ],
                default="hospital_staff",
                max_length=30,
            ),
        ),
    ]

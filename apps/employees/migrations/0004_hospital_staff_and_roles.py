# Renames EmployeeProfile → HospitalStaff and physical table employee_profiles → hospital_staff
# without dropping data.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0003_alter_employeeprofile_department_and_more"),
        ("hospital_directory", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    state_operations = [
        migrations.RenameModel(old_name="EmployeeProfile", new_name="HospitalStaff"),
        migrations.AlterModelTable(name="hospitalstaff", table="hospital_staff"),
        migrations.AlterField(
            model_name="hospitalstaff",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="hospital_staff_profile",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="hospitalstaff",
            name="department",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="hospital_staff_members",
                to="hospital_directory.department",
            ),
        ),
        migrations.AlterField(
            model_name="hospitalstaff",
            name="designation",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="hospital_staff_members",
                to="hospital_directory.designation",
            ),
        ),
        migrations.AlterField(
            model_name="hospitalstaff",
            name="working_site",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="hospital_staff_members",
                to="hospital_directory.workingsite",
            ),
        ),
    ]

    database_operations = [
        migrations.RunSQL(
            sql='ALTER TABLE "employee_profiles" RENAME TO "hospital_staff";',
            reverse_sql='ALTER TABLE "hospital_staff" RENAME TO "employee_profiles";',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations,
        ),
    ]

# Generated manually — audit field for Top Management feedback dispatch

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0009_change_request_internal_targets"),
    ]

    operations = [
        migrations.AddField(
            model_name="reviewtrail",
            name="feedback_target",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Top Management only: who received this feedback (adr, hod, staff) or empty for final applicant approval.",
                max_length=20,
            ),
        ),
    ]

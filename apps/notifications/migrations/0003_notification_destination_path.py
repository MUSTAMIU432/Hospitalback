from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="destination_path",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Optional frontend route to open when user clicks notification.",
                max_length=255,
            ),
        ),
    ]

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0004_notification_sender"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                help_text="Root notification this message is a reply to (null = root).",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="replies",
                to="notifications.notification",
            ),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["parent"], name="notif_parent_idx"),
        ),
    ]

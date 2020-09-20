from django.db import migrations, models
import jsonfield.fields
from django.conf import settings
import inthe_am.taskmanager.models.taskattachment


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Announcement",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                (
                    "category",
                    models.CharField(
                        max_length=10,
                        choices=[
                            (b"error", b"Error"),
                            (b"notice", b"Info"),
                            (b"warning", b"Warning"),
                        ],
                    ),
                ),
                (
                    "duration",
                    models.PositiveIntegerField(default=300, help_text=b"In seconds"),
                ),
                ("message", models.TextField()),
                ("starts", models.DateTimeField()),
                ("expires", models.DateTimeField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="BugwarriorConfig",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("serialized_config", models.TextField()),
                ("enabled", models.BooleanField(default=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="BugwarriorConfigRunLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("success", models.BooleanField(default=False)),
                ("output", models.TextField()),
                ("stack_trace", models.TextField()),
                ("started", models.DateTimeField()),
                ("finished", models.DateTimeField(null=True)),
                (
                    "config",
                    models.ForeignKey(
                        related_name="run_logs", to="taskmanager.BugwarriorConfig"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TaskAttachment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("task_id", models.CharField(max_length=36)),
                ("name", models.CharField(max_length=256)),
                ("size", models.PositiveIntegerField()),
                (
                    "document",
                    models.FileField(
                        upload_to=inthe_am.taskmanager.models.taskattachment.get_attachment_path
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="TaskStore",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("local_path", models.CharField(max_length=255, blank=True)),
                ("configured", models.BooleanField(default=False)),
                ("secret_id", models.CharField(max_length=36, blank=True)),
                ("sync_enabled", models.BooleanField(default=True)),
                ("sync_permitted", models.BooleanField(default=True)),
                ("pebble_cards_enabled", models.BooleanField(default=False)),
                ("feed_enabled", models.BooleanField(default=False)),
                ("ical_enabled", models.BooleanField(default=False)),
                ("taskrc_extras", models.TextField(blank=True)),
                ("twilio_auth_token", models.CharField(max_length=32, blank=True)),
                ("trello_auth_token", models.CharField(max_length=200, blank=True)),
                ("trello_local_head", models.CharField(max_length=100, blank=True)),
                ("sms_whitelist", models.TextField(blank=True)),
                ("sms_arguments", models.TextField(blank=True)),
                (
                    "sms_replies",
                    models.PositiveIntegerField(
                        default=9,
                        choices=[
                            (9, b"Reply to all messages"),
                            (5, b"Reply only to error messages"),
                            (0, b"Do not reply to any incoming text messages"),
                        ],
                    ),
                ),
                ("email_whitelist", models.TextField(blank=True)),
                ("last_synced", models.DateTimeField(null=True, blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        related_name="task_stores",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TaskStoreActivity",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("activity", models.CharField(max_length=255)),
                ("metadata_version", models.CharField(default=b"v5", max_length=10)),
                ("message", models.TextField(blank=True)),
                ("metadata", jsonfield.fields.JSONField(null=True, blank=True)),
                ("duration_seconds", models.FloatField(null=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("started", models.DateTimeField(auto_now_add=True)),
                (
                    "store",
                    models.ForeignKey(related_name="syncs", to="taskmanager.TaskStore"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TaskStoreActivityLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("md5hash", models.CharField(max_length=32)),
                ("last_seen", models.DateTimeField(auto_now=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("error", models.BooleanField(default=False)),
                ("silent", models.BooleanField(default=False)),
                ("message", models.TextField()),
                ("count", models.IntegerField(default=0)),
                (
                    "store",
                    models.ForeignKey(
                        related_name="log_entries", to="taskmanager.TaskStore"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TrelloObject",
            fields=[
                (
                    "id",
                    models.CharField(max_length=100, serialize=False, primary_key=True),
                ),
                (
                    "type",
                    models.CharField(
                        max_length=10,
                        choices=[
                            (b"card", b"Card"),
                            (b"board", b"Board"),
                            (b"list", b"List"),
                        ],
                    ),
                ),
                ("meta", jsonfield.fields.JSONField()),
                ("log", jsonfield.fields.JSONField(null=True, blank=True)),
                ("deleted", models.BooleanField(default=False)),
                ("last_action", models.DateTimeField(null=True, blank=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "parent",
                    models.ForeignKey(
                        related_name="children",
                        blank=True,
                        to="taskmanager.TrelloObject",
                        null=True,
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        related_name="trello_objects", to="taskmanager.TaskStore"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TrelloObjectAction",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("type", models.CharField(max_length=100)),
                ("action_id", models.CharField(max_length=100)),
                ("meta", jsonfield.fields.JSONField()),
                ("occurred", models.DateTimeField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "model",
                    models.ForeignKey(
                        related_name="actions",
                        blank=True,
                        to="taskmanager.TrelloObject",
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserMetadata",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("tos_version", models.IntegerField(default=0)),
                ("tos_accepted", models.DateTimeField(default=None, null=True)),
                (
                    "colorscheme",
                    models.CharField(
                        default=b"dark-yellow-green.theme", max_length=255
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        related_name="metadata",
                        to=settings.AUTH_USER_MODEL,
                        unique=True,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="taskattachment",
            name="store",
            field=models.ForeignKey(
                related_name="attachments", to="taskmanager.TaskStore"
            ),
        ),
        migrations.AddField(
            model_name="bugwarriorconfig",
            name="store",
            field=models.ForeignKey(
                related_name="bugwarrior_configs", to="taskmanager.TaskStore"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="taskstoreactivitylog", unique_together={("store", "md5hash")},
        ),
    ]

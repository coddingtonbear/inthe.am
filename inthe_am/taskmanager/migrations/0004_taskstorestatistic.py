from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taskmanager", "0003_resthook"),
    ]

    operations = [
        migrations.CreateModel(
            name="TaskStoreStatistic",
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
                (
                    "measure",
                    models.CharField(
                        max_length=50, choices=[(b"size", b"Repository Size")]
                    ),
                ),
                ("value", models.BigIntegerField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "store",
                    models.ForeignKey(
                        related_name="statistics", to="taskmanager.TaskStore"
                    ),
                ),
            ],
        ),
    ]

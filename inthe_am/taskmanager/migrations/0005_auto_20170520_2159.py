from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taskmanager", "0004_taskstorestatistic"),
    ]

    operations = [
        migrations.AddField(
            model_name="taskstorestatistic",
            name="run_id",
            field=models.CharField(
                default=None,
                help_text=b"If generated by an automated process, indicates the job name used for generating this value.",
                max_length=255,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="taskstorestatistic",
            name="value",
            field=models.FloatField(),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taskmanager", "0005_auto_20170520_2159"),
    ]

    operations = [
        migrations.AddField(
            model_name="usermetadata",
            name="privacy_policy_accepted",
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="usermetadata",
            name="privacy_policy_version",
            field=models.IntegerField(default=0),
        ),
    ]

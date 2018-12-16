# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskmanager', '0006_auto_20180524_0418'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bugwarriorconfig',
            name='store',
        ),
        migrations.RemoveField(
            model_name='bugwarriorconfigrunlog',
            name='config',
        ),
        migrations.DeleteModel(
            name='BugwarriorConfig',
        ),
        migrations.DeleteModel(
            name='BugwarriorConfigRunLog',
        ),
    ]

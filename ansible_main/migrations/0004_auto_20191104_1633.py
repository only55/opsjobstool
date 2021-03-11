# Generated by Django 2.2.6 on 2019-11-04 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ansible_main', '0003_usertask_task_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventlog',
            name='task_name',
        ),
        migrations.AddField(
            model_name='eventlog',
            name='task_log',
            field=models.CharField(default=1, max_length=1000),
            preserve_default=False,
        ),
    ]

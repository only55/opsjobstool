# Generated by Django 3.0 on 2020-01-07 11:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ansible_main', '0010_auto_20191231_2010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventlog',
            name='task_id',
        ),
        migrations.AddField(
            model_name='eventlog',
            name='exec_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ansible_main.ExecTask'),
            preserve_default=False,
        ),
    ]

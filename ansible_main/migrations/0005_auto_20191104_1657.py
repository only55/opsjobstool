# Generated by Django 2.2.6 on 2019-11-04 08:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ansible_main', '0004_auto_20191104_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertaskcommand',
            name='task_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ansible_main.User'),
        ),
    ]

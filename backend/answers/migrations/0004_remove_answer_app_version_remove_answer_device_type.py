# Generated by Django 4.0.5 on 2023-01-26 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('answers', '0003_rename_device_id_answer_user_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='app_version',
        ),
        migrations.RemoveField(
            model_name='answer',
            name='device_type',
        ),
    ]
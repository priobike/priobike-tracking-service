# Generated by Django 4.0.5 on 2022-08-29 11:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_id', models.TextField(max_length=100)),
                ('device_type', models.TextField(max_length=100)),
                ('app_version', models.TextField(max_length=20)),
                ('question_text', models.TextField(max_length=300)),
                ('question_image', models.TextField(blank=True, max_length=10000000, null=True)),
                ('session_id', models.TextField(blank=True, max_length=100, null=True)),
                ('value', models.TextField(blank=True, max_length=1000, null=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
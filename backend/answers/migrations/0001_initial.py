# Generated by Django 4.2.13 on 2024-05-13 07:35

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
                ('session_id', models.CharField(default='unknown', max_length=255, primary_key=True, serialize=False)),
                ('user_id', models.TextField(max_length=100)),
                ('question_text', models.TextField(max_length=300)),
                ('question_image', models.TextField(blank=True, max_length=10000000, null=True)),
                ('value', models.TextField(blank=True, max_length=1000, null=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Answer',
                'verbose_name_plural': 'Answers',
                'ordering': ['-date'],
            },
        ),
    ]

# Generated by Django 4.2.23 on 2025-07-17 04:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_question_creator'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='close_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='open_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

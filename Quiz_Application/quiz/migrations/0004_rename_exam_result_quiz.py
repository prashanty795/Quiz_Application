# Generated by Django 5.0.4 on 2024-04-11 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_result_staff'),
    ]

    operations = [
        migrations.RenameField(
            model_name='result',
            old_name='exam',
            new_name='quiz',
        ),
    ]

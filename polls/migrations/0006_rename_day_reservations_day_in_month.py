# Generated by Django 3.2.8 on 2022-05-05 21:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0005_cancel_request_response_to_request'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reservations',
            old_name='day',
            new_name='day_in_month',
        ),
    ]

# Generated by Django 3.2.8 on 2022-05-11 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0007_remove_res_done_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person_reduce_shift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fname', models.CharField(max_length=200)),
                ('lname', models.CharField(max_length=200)),
                ('number_of_shift', models.CharField(max_length=200)),
            ],
        ),
    ]

# Generated by Django 3.2.8 on 2022-03-14 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fname', models.CharField(max_length=200)),
                ('lname', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=200)),
                ('password', models.CharField(max_length=200)),
                ('username', models.CharField(max_length=200)),
                ('gender', models.CharField(max_length=200, null=True)),
                ('rank', models.CharField(max_length=200, null=True)),
                ('camp', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='res_date',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reservations_id', models.CharField(max_length=200)),
                ('date', models.CharField(max_length=200)),
                ('person1_id', models.CharField(max_length=200)),
                ('person2_id', models.CharField(max_length=200)),
                ('person3_id', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='reservations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(max_length=200)),
                ('shift_time', models.CharField(max_length=200)),
            ],
        ),
    ]

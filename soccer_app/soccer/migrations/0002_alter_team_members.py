# Generated by Django 4.1.3 on 2022-11-23 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('soccer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(to='soccer.user'),
        ),
    ]

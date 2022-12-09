# Generated by Django 4.1.3 on 2022-11-26 21:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('soccer', '0006_alter_game_team_num'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='team_num',
            field=models.IntegerField(default=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)]),
        ),
    ]

# Generated by Django 4.1.3 on 2022-11-26 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('soccer', '0004_rename_organizer_game_organizers'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='team_num',
            field=models.IntegerField(default=2),
        ),
    ]

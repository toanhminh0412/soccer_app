# Generated by Django 4.1.3 on 2022-11-26 04:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('soccer', '0003_game_location'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='organizer',
            new_name='organizers',
        ),
    ]

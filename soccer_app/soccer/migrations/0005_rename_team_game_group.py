# Generated by Django 4.1.3 on 2022-12-28 22:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('soccer', '0004_remove_socceruser_confirmation_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='team',
            new_name='group',
        ),
    ]
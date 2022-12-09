# Generated by Django 4.1.3 on 2022-11-23 04:58

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('date', models.DateTimeField()),
                ('max_player_num', models.IntegerField(blank=True, null=True)),
                ('visible_to_everyone', models.BooleanField(default=True)),
                ('description', models.CharField(max_length=300)),
            ],
            options={
                'db_table': 'soccer_team_game',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('max_member_num', models.IntegerField(blank=True, null=True)),
                ('description', models.CharField(max_length=300)),
            ],
            options={
                'db_table': 'soccer_team',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(regex='[0-9]{10}')])),
                ('name', models.CharField(max_length=30)),
                ('last_active', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'soccer_user',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TeamAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('captain', models.BooleanField()),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='soccer.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='soccer.user')),
            ],
            options={
                'db_table': 'soccer_team_admin',
                'ordering': ['user'],
            },
        ),
        migrations.AddField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(blank=True, null=True, to='soccer.user'),
        ),
        migrations.CreateModel(
            name='GameTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_number', models.IntegerField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='soccer.game')),
                ('players', models.ManyToManyField(to='soccer.user')),
            ],
            options={
                'db_table': 'soccer_game_team',
                'ordering': ['game'],
            },
        ),
        migrations.AddField(
            model_name='game',
            name='organizer',
            field=models.ManyToManyField(to='soccer.user'),
        ),
        migrations.AddField(
            model_name='game',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='soccer.team'),
        ),
    ]

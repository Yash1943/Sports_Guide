# Generated by Django 5.0.2 on 2025-04-18 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0011_player_team_alter_team_players'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='team',
        ),
        migrations.AlterField(
            model_name='team',
            name='players',
            field=models.ManyToManyField(to='authentication.player'),
        ),
    ]

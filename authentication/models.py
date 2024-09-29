from django.db import models
from django.utils import timezone

class Sport(models.Model):
    id = models.IntegerField(primary_key=True)
    sport_name = models.CharField(max_length=100)

    def _str_(self):
        return self.sport_name
    
# class Session(models.Model):
#     sport_name = models.CharField(max_length=100)
#     venue = models.CharField(max_length=100)
#     number_of_teams = models.IntegerField()
#     time = models.DateTimeField()

# models.py
from django.db import models

class Session(models.Model):
    sport_name = models.CharField(max_length=100)
    venue = models.CharField(max_length=100)
    number_of_teams = models.IntegerField()
    time = models.DateTimeField()

    def _str_(self):
        return f"{self.sport_name} at {self.venue} on {self.time}"

class PlayerType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def _str_(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=100)
    player_type = models.ForeignKey(PlayerType, on_delete=models.CASCADE, related_name='players')

    def _str_(self):
        return self.name

class Team(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    players = models.ManyToManyField(Player)

    def _str_(self):
        return f"Team {self.name} for {self.session.sport_name}"
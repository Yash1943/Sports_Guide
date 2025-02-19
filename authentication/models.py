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
    
from django.db import models

class Player_reco(models.Model):
    ROLE_CHOICES = [
        ('batsman', 'Batsman'),
        ('bowler', 'Bowler'),
        ('allrounder', 'All-rounder'),
        ('wicketkeeper', 'Wicketkeeper'),
    ]

    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    team = models.CharField(max_length=100, blank=True, null=True)  # Optional team name
    age = models.IntegerField(default=18)
    nationality = models.CharField(max_length=50, default="Unknown")

    def __str__(self):
        return f"{self.name} ({self.role})"

class PlayerStats(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)

    # Batting stats
    batting_average = models.FloatField(default=0.0)
    strike_rate = models.FloatField(default=0.0)
    total_runs = models.IntegerField(default=0)

    # Bowling stats
    wickets = models.IntegerField(default=0)
    bowling_average = models.FloatField(default=0.0)
    economy = models.FloatField(default=0.0)
    
    # Additional stats (Optional)
    matches_played = models.IntegerField(default=0)
    highest_score = models.IntegerField(default=0)
    best_bowling_figures = models.CharField(max_length=20, blank=True, null=True)  # Example: "5/30"

    def __str__(self):
        return f"Stats for {self.player.name}"

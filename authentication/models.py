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

    # New fields for AI model
    recent_form = models.FloatField(default=0.0)  # Recent performance (1-10 scale)
    fitness_level = models.FloatField(default=0.0)  # Player fitness rating
    match_experience = models.IntegerField(default=0)  # Number of matches played

    def __str__(self):
        return f"Stats for {self.player.name}"

class Match(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team1_matches')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team2_matches')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name} on {self.date}"

class TeamComposition(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    players = models.ManyToManyField(Player)
    is_team1 = models.BooleanField()  # True for team1, False for team2

    def __str__(self):
        return f"Team composition for {self.team.name} in {self.match}"


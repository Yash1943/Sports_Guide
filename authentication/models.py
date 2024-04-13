from django.db import models
from django.utils import timezone

class Sport(models.Model):
    id = models.IntegerField(primary_key=True)
    sport_name = models.CharField(max_length=100)

    def __str__(self):
        return self.sport_name
    
class Session(models.Model):
    sport_name = models.CharField(max_length=100)
    venue = models.CharField(max_length=100)
    number_of_teams = models.IntegerField()
    time = models.DateTimeField()
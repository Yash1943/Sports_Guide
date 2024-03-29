from django.db import models

class sports(models.Model):
    id = models.IntegerField(primary_key=True)
    sport_name = models.CharField(max_length=100)
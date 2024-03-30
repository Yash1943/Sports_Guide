from django.db import models

class Sport(models.Model):
    id = models.IntegerField(primary_key=True)
    sport_name = models.CharField(max_length=100)

    def __str__(self):
        return self.sport_name

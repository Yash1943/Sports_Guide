from django.contrib import admin
from authentication.models import Sport
from authentication.models import Session
from authentication.models import PlayerType
from authentication.models import Player
from authentication.models import Team

# Register your models here.
admin.site.register(Sport)
admin.site.register(Session)
admin.site.register(PlayerType)
admin.site.register(Player)
admin.site.register(Team)
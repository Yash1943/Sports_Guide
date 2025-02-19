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

from django.contrib import admin
from .models import Player_reco, PlayerStats

@admin.register(Player_reco)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'team', 'age', 'nationality')
    search_fields = ('name', 'team')

@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = ('player', 'batting_average', 'strike_rate', 'total_runs', 'wickets', 'bowling_average', 'economy')
    search_fields = ('player__name',)

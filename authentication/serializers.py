from rest_framework import serializers
from .models import Player_reco, PlayerStats

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player_reco
        fields = '__all__'

class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = '__all__'

from rest_framework import serializers
from authentication.models import Player, PlayerStats

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = "__all__"

class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = "__all__"


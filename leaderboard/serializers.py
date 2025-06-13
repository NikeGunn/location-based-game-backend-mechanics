from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import LeaderboardEntry

User = get_user_model()


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    level = serializers.IntegerField(source='user.level', read_only=True)

    class Meta:
        model = LeaderboardEntry
        fields = ['rank', 'username', 'level', 'score', 'last_updated']


class UserRankSerializer(serializers.Serializer):
    category = serializers.CharField()
    rank = serializers.IntegerField()
    score = serializers.IntegerField()
    total_users = serializers.IntegerField()
    percentile = serializers.FloatField()


class LeaderboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_zones = serializers.IntegerField()
    total_attacks = serializers.IntegerField()
    most_active_zone = serializers.CharField()
    top_player = serializers.CharField()


class DetailedUserStatsSerializer(serializers.ModelSerializer):
    zones_owned_count = serializers.IntegerField(source='zones_owned')
    attacks_made = serializers.SerializerMethodField()
    attacks_won = serializers.SerializerMethodField()
    defenses_made = serializers.SerializerMethodField()
    defenses_won = serializers.SerializerMethodField()
    attack_success_rate = serializers.SerializerMethodField()
    defense_success_rate = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'username', 'level', 'xp', 'zones_owned_count',
            'attacks_made', 'attacks_won', 'defenses_made', 'defenses_won',
            'attack_success_rate', 'defense_success_rate'
        ]

    def get_attacks_made(self, obj):
        return obj.attacks_made.count()

    def get_attacks_won(self, obj):
        return obj.attacks_made.filter(success=True).count()

    def get_defenses_made(self, obj):
        return obj.attacks_received.count()

    def get_defenses_won(self, obj):
        return obj.attacks_received.filter(success=False).count()

    def get_attack_success_rate(self, obj):
        total = self.get_attacks_made(obj)
        won = self.get_attacks_won(obj)
        return round((won / total * 100), 1) if total > 0 else 0

    def get_defense_success_rate(self, obj):
        total = self.get_defenses_made(obj)
        won = self.get_defenses_won(obj)
        return round((won / total * 100), 1) if total > 0 else 0

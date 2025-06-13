from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import Attack, AttackCooldown


class AttackSerializer(serializers.Serializer):
    zone_id = serializers.CharField(max_length=50)
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)

    def validate(self, attrs):
        attrs['attacker_location'] = Point(attrs['longitude'], attrs['latitude'])
        return attrs


class AttackResultSerializer(serializers.ModelSerializer):
    attacker_username = serializers.CharField(source='attacker.username', read_only=True)
    defender_username = serializers.CharField(source='defender.username', read_only=True, allow_null=True)
    zone_id = serializers.CharField(source='zone.id', read_only=True)
    latitude = serializers.FloatField(source='attacker_location.y', read_only=True)
    longitude = serializers.FloatField(source='attacker_location.x', read_only=True)

    class Meta:
        model = Attack
        fields = [
            'id', 'attacker_username', 'defender_username', 'zone_id',
            'attacker_power', 'defender_power', 'result', 'success',
            'latitude', 'longitude', 'xp_gained', 'timestamp'
        ]


class AttackHistorySerializer(serializers.ModelSerializer):
    opponent_username = serializers.SerializerMethodField()
    zone_id = serializers.CharField(source='zone.id', read_only=True)

    class Meta:
        model = Attack
        fields = [
            'id', 'opponent_username', 'zone_id', 'attacker_power',
            'defender_power', 'result', 'success', 'xp_gained', 'timestamp'
        ]

    def get_opponent_username(self, obj):
        # For attacks made by user, show defender
        if obj.attacker == self.context['user']:
            return obj.defender.username if obj.defender else 'Unclaimed Zone'
        # For attacks received by user, show attacker
        else:
            return obj.attacker.username


class CooldownStatusSerializer(serializers.ModelSerializer):
    zone_id = serializers.CharField(source='zone.id', read_only=True)
    is_on_cooldown = serializers.BooleanField(read_only=True)

    class Meta:
        model = AttackCooldown
        fields = ['zone_id', 'last_attack', 'cooldown_until', 'is_on_cooldown']

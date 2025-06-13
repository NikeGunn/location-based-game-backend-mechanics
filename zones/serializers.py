from rest_framework import serializers
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.conf import settings
from .models import Zone, ZoneCheckIn


class ZoneSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(source='location.y', read_only=True)
    longitude = serializers.FloatField(source='location.x', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True, allow_null=True)
    is_claimed = serializers.BooleanField(read_only=True)
    defense_power = serializers.IntegerField(read_only=True)

    class Meta:
        model = Zone
        fields = [
            'id', 'latitude', 'longitude', 'owner_username', 'is_claimed',
            'claimed_at', 'expires_at', 'xp_value', 'defense_power'
        ]
        read_only_fields = ['id', 'claimed_at', 'expires_at']


class NearbyZonesSerializer(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    radius = serializers.IntegerField(min_value=100, max_value=5000, default=1000)  # meters

    def validate(self, attrs):
        attrs['location'] = Point(attrs['longitude'], attrs['latitude'])
        return attrs


class ZoneCheckInSerializer(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    zone_id = serializers.CharField(max_length=50, required=False)

    def validate(self, attrs):
        user_location = Point(attrs['longitude'], attrs['latitude'])
        attrs['user_location'] = user_location

        # If zone_id not provided, generate it
        if not attrs.get('zone_id'):
            attrs['zone_id'] = Zone.generate_zone_id(attrs['latitude'], attrs['longitude'])

        return attrs

    def validate_location(self, user_location, zone_location):
        """Validate user is within capture radius of zone"""
        distance = user_location.distance(zone_location) * 111000  # Convert to meters
        if distance > settings.ZONE_CAPTURE_RADIUS_METERS:
            raise serializers.ValidationError(
                f"You must be within {settings.ZONE_CAPTURE_RADIUS_METERS}m of the zone to check in"
            )
        return True


class ZoneCheckInResponseSerializer(serializers.ModelSerializer):
    zone = ZoneSerializer(read_only=True)
    latitude = serializers.FloatField(source='location.y', read_only=True)
    longitude = serializers.FloatField(source='location.x', read_only=True)

    class Meta:
        model = ZoneCheckIn
        fields = ['zone', 'latitude', 'longitude', 'timestamp', 'success']

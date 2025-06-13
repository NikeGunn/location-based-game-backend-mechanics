import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from zones.models import Zone
from zones.services import ZoneService

User = get_user_model()


@pytest.mark.django_db
class TestZoneService:
    def test_zone_creation(self):
        """Test zone creation and claiming"""
        user = User.objects.create_user(username='testuser', password='testpass')
        zone_id = 'test_zone_123'
        location = Point(-122.4194, 37.7749)  # San Francisco

        zone, created = ZoneService.get_or_create_zone(zone_id, 37.7749, -122.4194)

        assert created is True
        assert zone.id == zone_id
        assert zone.location.equals(location)

    def test_zone_claiming(self):
        """Test zone claiming logic"""
        user = User.objects.create_user(username='testuser', password='testpass')
        zone = Zone.objects.create(
            id='test_zone',
            location=Point(-122.4194, 37.7749)
        )

        # Test unclaimed zone
        assert not zone.is_claimed

        # Claim zone
        zone.claim(user)

        assert zone.is_claimed
        assert zone.owner == user
        assert zone.claimed_at is not None
        assert zone.expires_at is not None

    def test_nearby_zones(self):
        """Test getting nearby zones"""
        # Create test zones
        Zone.objects.create(id='zone1', location=Point(-122.4194, 37.7749))
        Zone.objects.create(id='zone2', location=Point(-122.4180, 37.7750))
        Zone.objects.create(id='zone3', location=Point(-122.0000, 37.0000))  # Far away

        user_location = Point(-122.4194, 37.7749)
        nearby_zones = ZoneService.get_nearby_zones(user_location, radius_meters=200)

        assert nearby_zones.count() == 2  # Should not include far away zone

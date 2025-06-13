import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from zones.models import Zone
from attacks.models import Attack
from attacks.services import AttackService

User = get_user_model()


@pytest.mark.django_db
class TestAttackService:
    def test_attack_validation(self):
        """Test attack validation logic"""
        attacker = User.objects.create_user(username='attacker', password='testpass')
        defender = User.objects.create_user(username='defender', password='testpass')

        zone = Zone.objects.create(
            id='test_zone',
            location=Point(-122.4194, 37.7749),
            owner=defender
        )
        zone.claim(defender)

        # Valid attack location (within radius)
        attack_location = Point(-122.4194, 37.7749)

        # Should not raise exception
        validated_zone = AttackService.validate_attack(attacker, zone.id, attack_location)
        assert validated_zone == zone

    def test_attack_own_zone_fails(self):
        """Test that users cannot attack their own zones"""
        user = User.objects.create_user(username='testuser', password='testpass')
        zone = Zone.objects.create(
            id='test_zone',
            location=Point(-122.4194, 37.7749),
            owner=user
        )
        zone.claim(user)

        attack_location = Point(-122.4194, 37.7749)

        with pytest.raises(ValueError, match="You cannot attack your own zone"):
            AttackService.validate_attack(user, zone.id, attack_location)

    def test_battle_outcome_calculation(self):
        """Test battle outcome calculation"""
        attacker = User.objects.create_user(username='attacker', password='testpass', level=5)
        defender = User.objects.create_user(username='defender', password='testpass', level=3)

        zone = Zone.objects.create(
            id='test_zone',
            location=Point(-122.4194, 37.7749),
            owner=defender
        )
        zone.claim(defender)

        outcome = AttackService.calculate_battle_outcome(attacker, zone)

        assert 'success' in outcome
        assert 'attacker_power' in outcome
        assert 'defender_power' in outcome
        assert 'xp_gained' in outcome
        assert isinstance(outcome['success'], bool)

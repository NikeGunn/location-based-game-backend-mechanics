import random
from django.contrib.gis.geos import Point
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from zones.models import Zone
from zones.services import ZoneService
from utils.notifications import send_zone_attack_notification_task, send_zone_result_notification_task
from .models import Attack, AttackCooldown

User = get_user_model()


class AttackService:
    """Service class for attack-related business logic"""

    @staticmethod
    def validate_attack(attacker, zone_id, attacker_location):
        """Validate if attack is allowed"""
        try:
            zone = Zone.objects.select_related('owner').get(id=zone_id)
        except Zone.DoesNotExist:
            raise ValueError("Zone not found")

        # Check if user is trying to attack their own zone
        if zone.owner == attacker:
            raise ValueError("You cannot attack your own zone")

        # Check if zone is unclaimed
        if not zone.is_claimed:
            raise ValueError("Zone is not claimed by anyone")

        # Validate location
        if not ZoneService.validate_user_location(attacker_location, zone.location):
            raise ValueError(f"You must be within {settings.ZONE_CAPTURE_RADIUS_METERS}m of the zone to attack")

        # Check cooldown
        cooldown = AttackCooldown.objects.filter(
            user=attacker,
            zone=zone
        ).first()

        if cooldown and cooldown.is_on_cooldown:
            remaining_minutes = int((cooldown.cooldown_until - timezone.now()).total_seconds() / 60)
            raise ValueError(f"Attack on cooldown. Try again in {remaining_minutes} minutes")

        return zone

    @staticmethod
    def calculate_battle_outcome(attacker, zone):
        """Calculate battle outcome based on various factors"""
        attacker_power = attacker.attack_power
        defender_power = zone.defense_power

        # Add some randomness (±20%)
        attacker_roll = attacker_power * (0.8 + random.random() * 0.4)
        defender_roll = defender_power * (0.8 + random.random() * 0.4)

        # Attacker wins if their roll is higher
        success = attacker_roll > defender_roll

        # XP calculation based on difficulty
        base_xp = zone.xp_value
        if success:
            # More XP for successful attacks
            xp_gained = base_xp + int(defender_power * 0.1)
        else:
            # Small XP for failed attempts
            xp_gained = max(1, base_xp // 4)

        return {
            'success': success,
            'attacker_power': int(attacker_roll),
            'defender_power': int(defender_roll),
            'xp_gained': xp_gained
        }

    @staticmethod
    def execute_attack(attacker, zone_id, attacker_location):
        """Execute an attack on a zone"""
        # Validate attack
        zone = AttackService.validate_attack(attacker, zone_id, attacker_location)

        # Calculate battle outcome
        battle_result = AttackService.calculate_battle_outcome(attacker, zone)

        # Create attack record
        attack = Attack.objects.create(
            attacker=attacker,
            defender=zone.owner,
            zone=zone,
            attacker_power=battle_result['attacker_power'],
            defender_power=battle_result['defender_power'],
            result='success' if battle_result['success'] else 'failed',
            success=battle_result['success'],
            attacker_location=attacker_location,
            xp_gained=battle_result['xp_gained']
        )
          # Update user XP
        ZoneService.update_user_stats(attacker, battle_result['xp_gained'])

        # Send notifications
        if zone.owner:
            # Send attack notification to defender
            send_zone_attack_notification_task.delay(
                zone.owner.id, zone_id, attacker.username
            )

        # If attack successful, transfer zone ownership
        if battle_result['success']:
            old_owner = zone.owner
            zone.claim(attacker)

            # Update both users' zone counts
            if old_owner:
                ZoneService.update_user_stats(old_owner, 0)  # Just update count
                # Send zone lost notification
                send_zone_result_notification_task.delay(
                    old_owner.id, zone_id, attacker.username, True
                )
            ZoneService.update_user_stats(attacker, 0)  # Just update count
        else:
            # Attack failed, send defended notification
            if zone.owner:
                send_zone_result_notification_task.delay(
                    zone.owner.id, zone_id, attacker.username, False
                )

        # Set cooldown
        AttackCooldown.set_cooldown(
            attacker,
            zone,
            minutes=settings.ATTACK_COOLDOWN_MINUTES
        )

        return attack

    @staticmethod
    def get_user_attack_history(user, limit=50):
        """Get user's attack history (both made and received)"""
        attacks_made = Attack.objects.filter(attacker=user)
        attacks_received = Attack.objects.filter(defender=user)

        # Combine and sort by timestamp
        all_attacks = list(attacks_made) + list(attacks_received)
        all_attacks.sort(key=lambda x: x.timestamp, reverse=True)

        return all_attacks[:limit]

    @staticmethod
    def get_user_cooldowns(user):
        """Get all active cooldowns for a user"""
        return AttackCooldown.objects.filter(
            user=user,
            cooldown_until__gt=timezone.now()
        ).select_related('zone')

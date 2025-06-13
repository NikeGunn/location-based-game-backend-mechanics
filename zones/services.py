from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from .models import Zone, ZoneCheckIn
from .tasks import schedule_zone_expiry

User = get_user_model()


class ZoneService:
    """Service class for zone-related business logic"""

    @staticmethod
    def get_nearby_zones(user_location, radius_meters=1000):
        """Get zones within specified radius of user location"""
        return Zone.objects.filter(
            location__distance_lte=(user_location, Distance(m=radius_meters))
        ).select_related('owner')

    @staticmethod
    def get_or_create_zone(zone_id, latitude, longitude):
        """Get existing zone or create new one"""
        zone, created = Zone.objects.get_or_create(
            id=zone_id,
            defaults={
                'location': Point(longitude, latitude),
            }
        )
        return zone, created

    @staticmethod
    def validate_user_location(user_location, zone_location):
        """Validate user is within capture radius"""
        distance = user_location.distance(zone_location) * 111000  # Convert to meters
        return distance <= settings.ZONE_CAPTURE_RADIUS_METERS

    @staticmethod
    def check_in_to_zone(user, zone_id, user_location):
        """Handle zone check-in logic"""
        zone, created = ZoneService.get_or_create_zone(
            zone_id,
            user_location.y,
            user_location.x
        )

        # Validate location
        if not ZoneService.validate_user_location(user_location, zone.location):
            raise ValueError(f"You must be within {settings.ZONE_CAPTURE_RADIUS_METERS}m of the zone")

        # Create check-in record
        checkin = ZoneCheckIn.objects.create(
            user=user,
            zone=zone,
            location=user_location
        )

        # Handle zone claiming logic
        if not zone.is_claimed:
            # Zone is unclaimed, user can claim it
            zone.claim(user)
            ZoneService.update_user_stats(user, zone.xp_value)

            # Schedule zone expiry task
            schedule_zone_expiry.apply_async(
                args=[zone.id],
                eta=zone.expires_at
            )

            return checkin, "Zone claimed successfully!"

        elif zone.owner == user:
            # User already owns this zone
            return checkin, "You already own this zone"

        else:
            # Zone is owned by someone else - this is just a check-in
            return checkin, "Zone is owned by another player. Use attack to claim it!"

    @staticmethod
    def update_user_stats(user, xp_gained):
        """Update user XP, level, and zone count"""
        user.xp += xp_gained

        # Simple level calculation (every 100 XP = 1 level)
        new_level = (user.xp // 100) + 1
        if new_level > user.level:
            user.level = new_level

        # Update zones owned count
        user.zones_owned = user.owned_zones.filter(
            expires_at__gt=timezone.now()
        ).count()

        user.save(update_fields=['xp', 'level', 'zones_owned'])

    @staticmethod
    def expire_zone(zone_id):
        """Expire a zone and update owner's stats"""
        try:
            zone = Zone.objects.select_related('owner').get(id=zone_id)
            if zone.owner:
                zone.unclaim()
                # Update owner's zone count
                ZoneService.update_user_stats(zone.owner, 0)  # Just update count, no XP
        except Zone.DoesNotExist:
            pass

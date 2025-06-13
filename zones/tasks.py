from celery import shared_task
from django.utils import timezone
from .models import Zone


@shared_task
def schedule_zone_expiry(zone_id):
    """Task to expire a zone after 24 hours"""
    try:
        zone = Zone.objects.select_related('owner').get(id=zone_id)

        # Double check the zone hasn't already expired
        if zone.expires_at and timezone.now() >= zone.expires_at:
            if zone.owner:
                # Update user's zone count
                zone.owner.zones_owned = zone.owner.owned_zones.filter(
                    expires_at__gt=timezone.now()
                ).count() - 1  # Subtract this zone
                zone.owner.save(update_fields=['zones_owned'])

            zone.unclaim()
            return f"Zone {zone_id} expired successfully"

        return f"Zone {zone_id} not yet expired"

    except Zone.DoesNotExist:
        return f"Zone {zone_id} not found"


@shared_task
def cleanup_expired_zones():
    """Periodic task to clean up all expired zones"""
    expired_zones = Zone.objects.filter(
        expires_at__lt=timezone.now(),
        owner__isnull=False
    ).select_related('owner')

    count = 0
    for zone in expired_zones:
        if zone.owner:
            # Update user's zone count
            zone.owner.zones_owned = zone.owner.owned_zones.filter(
                expires_at__gt=timezone.now()
            ).count() - 1
            zone.owner.save(update_fields=['zones_owned'])

        zone.unclaim()
        count += 1

    return f"Cleaned up {count} expired zones"

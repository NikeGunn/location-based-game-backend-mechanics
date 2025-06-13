from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Zone(models.Model):
    """Represents a geographical zone that can be claimed by users"""
    id = models.CharField(max_length=50, primary_key=True)  # Grid-based ID like "zone_123_456"
    location = models.PointField()  # PostGIS Point field for lat/lng
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_zones')
    claimed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    xp_value = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Zone {self.id} - Owner: {self.owner.username if self.owner else 'Unclaimed'}"

    @property
    def is_claimed(self):
        """Check if zone is currently claimed and not expired"""
        if not self.owner or not self.expires_at:
            return False
        return timezone.now() < self.expires_at

    @property
    def defense_power(self):
        """Calculate zone's defense power based on owner's stats"""
        if not self.owner:
            return 0
        return self.owner.attack_power + 20  # Defender advantage

    def claim(self, user):
        """Claim this zone for a user"""
        from django.conf import settings
        self.owner = user
        self.claimed_at = timezone.now()
        self.expires_at = self.claimed_at + timedelta(hours=settings.ZONE_EXPIRY_HOURS)
        self.save()

    def unclaim(self):
        """Remove ownership of this zone"""
        self.owner = None
        self.claimed_at = None
        self.expires_at = None
        self.save()

    @classmethod
    def generate_zone_id(cls, lat, lng, grid_size=0.001):
        """Generate a zone ID based on lat/lng grid"""
        grid_lat = int(lat / grid_size)
        grid_lng = int(lng / grid_size)
        return f"zone_{grid_lat}_{grid_lng}"


class ZoneCheckIn(models.Model):
    """Records of user check-ins to zones"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='zone_checkins')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='checkins')
    location = models.PointField()  # User's actual location during check-in
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['zone', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} checked into {self.zone.id} at {self.timestamp}"

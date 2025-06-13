from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Attack(models.Model):
    """Records of zone attack attempts"""

    RESULT_CHOICES = [
        ('success', 'Successful Attack'),
        ('failed', 'Failed Attack'),
        ('cooldown', 'Attack on Cooldown'),
        ('invalid', 'Invalid Attack'),
    ]

    attacker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attacks_made')
    defender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attacks_received', null=True, blank=True)
    zone = models.ForeignKey('zones.Zone', on_delete=models.CASCADE, related_name='attacks')

    attacker_power = models.PositiveIntegerField()
    defender_power = models.PositiveIntegerField(default=0)

    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    success = models.BooleanField()

    attacker_location = models.PointField()  # Location of attacker during attack
    xp_gained = models.PositiveIntegerField(default=0)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['attacker', 'timestamp']),
            models.Index(fields=['zone', 'timestamp']),
            models.Index(fields=['defender', 'timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.attacker.username} attacked {self.zone.id} - {self.result}"


class AttackCooldown(models.Model):
    """Track attack cooldowns per user per zone"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    zone = models.ForeignKey('zones.Zone', on_delete=models.CASCADE)
    last_attack = models.DateTimeField(auto_now_add=True)
    cooldown_until = models.DateTimeField()

    class Meta:
        unique_together = ['user', 'zone']
        indexes = [
            models.Index(fields=['user', 'cooldown_until']),
        ]

    def __str__(self):
        return f"{self.user.username} cooldown for {self.zone.id} until {self.cooldown_until}"

    @property
    def is_on_cooldown(self):
        """Check if user is still on cooldown for this zone"""
        return timezone.now() < self.cooldown_until

    @classmethod
    def set_cooldown(cls, user, zone, minutes=30):
        """Set or update cooldown for user on specific zone"""
        cooldown_until = timezone.now() + timedelta(minutes=minutes)
        cooldown, created = cls.objects.update_or_create(
            user=user,
            zone=zone,
            defaults={
                'last_attack': timezone.now(),
                'cooldown_until': cooldown_until
            }
        )
        return cooldown

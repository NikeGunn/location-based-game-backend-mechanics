from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model with game-specific fields"""
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    zones_owned = models.PositiveIntegerField(default=0)
    push_token = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def attack_power(self):
        """Calculate user's attack power based on level and zones owned"""
        return self.level * 10 + min(self.zones_owned * 5, 50)

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class LeaderboardEntry(models.Model):
    """Cached leaderboard entries for performance"""

    CATEGORY_CHOICES = [
        ('xp', 'Experience Points'),
        ('zones', 'Zones Owned'),
        ('attacks', 'Successful Attacks'),
        ('level', 'User Level'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    score = models.PositiveIntegerField()
    rank = models.PositiveIntegerField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'category']
        indexes = [
            models.Index(fields=['category', 'rank']),
            models.Index(fields=['category', 'score']),
        ]
        ordering = ['category', 'rank']

    def __str__(self):
        return f"{self.user.username} - {self.category}: {self.score} (Rank {self.rank})"


class LeaderboardSnapshot(models.Model):
    """Store periodic snapshots of leaderboard data"""
    category = models.CharField(max_length=10, choices=LeaderboardEntry.CATEGORY_CHOICES)
    snapshot_date = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Store top users data

    class Meta:
        indexes = [
            models.Index(fields=['category', 'snapshot_date']),
        ]
        ordering = ['-snapshot_date']

    def __str__(self):
        return f"{self.category} leaderboard - {self.snapshot_date.date()}"

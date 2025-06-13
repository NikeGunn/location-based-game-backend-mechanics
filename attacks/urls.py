from django.urls import path
from .views import (
    AttackZoneView,
    AttackHistoryView,
    AttackCooldownView,
    AttackStatsView
)

urlpatterns = [
    path('', AttackZoneView.as_view(), name='attack_zone'),  # POST for attacks, GET for history
    path('cooldown/', AttackCooldownView.as_view(), name='attack_cooldown'),
    path('stats/', AttackStatsView.as_view(), name='attack_stats'),
]

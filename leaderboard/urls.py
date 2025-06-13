from django.urls import path
from .views import (
    LeaderboardView,
    UserRankView,
    UserStatsView,
    LeaderboardStatsView,
    RefreshLeaderboardView
)

urlpatterns = [
    path('', LeaderboardView.as_view(), name='leaderboard'),
    path('<str:category>/', LeaderboardView.as_view(), name='leaderboard_category'),
    path('my-rank/', UserRankView.as_view(), name='user_rank'),
    path('stats/', LeaderboardStatsView.as_view(), name='leaderboard_stats'),
    path('stats/<str:username>/', UserStatsView.as_view(), name='user_stats'),
    path('refresh/', RefreshLeaderboardView.as_view(), name='refresh_leaderboard'),
]

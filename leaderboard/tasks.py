from celery import shared_task
from .services import LeaderboardService


@shared_task
def update_leaderboards():
    """Periodic task to update all leaderboards"""
    categories = ['xp', 'zones', 'level', 'attacks']

    for category in categories:
        try:
            LeaderboardService.update_leaderboard(category)
            LeaderboardService.create_snapshot(category)
        except Exception as e:
            print(f"Error updating {category} leaderboard: {e}")

    return "Leaderboards updated successfully"


@shared_task
def update_single_leaderboard(category):
    """Update a specific leaderboard category"""
    try:
        LeaderboardService.update_leaderboard(category)
        return f"{category} leaderboard updated successfully"
    except Exception as e:
        return f"Error updating {category} leaderboard: {e}"

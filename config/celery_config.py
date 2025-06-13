from celery.schedules import crontab
from config.celery import app as celery_app

# Periodic task configuration
celery_app.conf.beat_schedule = {
    'cleanup-expired-zones': {
        'task': 'zones.tasks.cleanup_expired_zones',
        'schedule': crontab(minute=0),  # Every hour
    },
    'update-leaderboards': {
        'task': 'leaderboard.tasks.update_leaderboards',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
    },
}

celery_app.conf.timezone = 'UTC'

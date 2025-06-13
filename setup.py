#!/usr/bin/env python
"""
Setup script for the location-based game backend.
Run this after installing requirements to set up the database and initial data.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

def run_migrations():
    """Run database migrations"""
    print("Running database migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    print("✓ Migrations completed")

def create_superuser():
    """Create superuser if none exists"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if not User.objects.filter(is_superuser=True).exists():
        print("\nCreating superuser...")
        print("Please enter superuser details:")
        execute_from_command_line(['manage.py', 'createsuperuser'])
        print("✓ Superuser created")
    else:
        print("✓ Superuser already exists")

def load_sample_data():
    """Load sample zones for testing"""
    from zones.models import Zone
    from django.contrib.gis.geos import Point

    # Sample zones in San Francisco area
    sample_zones = [
        {'id': 'zone_37774_-122419', 'lat': 37.7749, 'lng': -122.4194},  # SF Downtown
        {'id': 'zone_37776_-122417', 'lat': 37.7764, 'lng': -122.4172},  # Union Square
        {'id': 'zone_37780_-122415', 'lat': 37.7804, 'lng': -122.4156},  # Chinatown
        {'id': 'zone_37783_-122408', 'lat': 37.7834, 'lng': -122.4083},  # North Beach
        {'id': 'zone_37769_-122413', 'lat': 37.7694, 'lng': -122.4131},  # SOMA
    ]

    created_count = 0
    for zone_data in sample_zones:
        zone, created = Zone.objects.get_or_create(
            id=zone_data['id'],
            defaults={
                'location': Point(zone_data['lng'], zone_data['lat']),
                'xp_value': 10
            }
        )
        if created:
            created_count += 1

    print(f"✓ Created {created_count} sample zones")

def update_leaderboards():
    """Initialize leaderboards"""
    from leaderboard.services import LeaderboardService

    print("Initializing leaderboards...")
    try:
        LeaderboardService.update_leaderboard()
        print("✓ Leaderboards initialized")
    except Exception as e:
        print(f"⚠ Leaderboard initialization failed: {e}")

def main():
    """Main setup function"""
    print("🎮 Setting up Location-Based Game Backend\n")

    # Setup Django
    setup_django()

    # Run migrations
    run_migrations()

    # Create superuser
    create_superuser()

    # Load sample data
    print("\nLoading sample data...")
    load_sample_data()

    # Initialize leaderboards
    update_leaderboards()

    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start Redis server")
    print("2. Run: python manage.py runserver")
    print("3. In another terminal: celery -A config worker -l info")
    print("4. In another terminal: celery -A config beat -l info")
    print("5. Visit http://localhost:8000/admin/ to access admin panel")

if __name__ == '__main__':
    main()

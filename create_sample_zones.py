"""
Script to create sample zone data for testing the game backend
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.gis.geos import Point
from zones.models import Zone

def create_sample_zones():
    """Create sample zones around a fictional city area"""

    # Clear existing zones
    Zone.objects.all().delete()
    print("Cleared existing zones")

    # Sample coordinates around a central point (fictional city)
    # Using coordinates around San Francisco as an example
    base_lat = 37.7749
    base_lng = -122.4194

    zones_data = [
        {"id": "zone_001", "lat": base_lat + 0.001, "lng": base_lng + 0.001},
        {"id": "zone_002", "lat": base_lat + 0.002, "lng": base_lng + 0.001},
        {"id": "zone_003", "lat": base_lat + 0.001, "lng": base_lng + 0.002},
        {"id": "zone_004", "lat": base_lat + 0.003, "lng": base_lng + 0.001},
        {"id": "zone_005", "lat": base_lat + 0.001, "lng": base_lng + 0.003},
        {"id": "zone_006", "lat": base_lat + 0.002, "lng": base_lng + 0.002},
        {"id": "zone_007", "lat": base_lat + 0.004, "lng": base_lng + 0.002},
        {"id": "zone_008", "lat": base_lat + 0.002, "lng": base_lng + 0.004},
        {"id": "zone_009", "lat": base_lat + 0.005, "lng": base_lng + 0.003},
        {"id": "zone_010", "lat": base_lat + 0.003, "lng": base_lng + 0.005},
    ]

    created_zones = []
    for zone_data in zones_data:
        point = Point(zone_data["lng"], zone_data["lat"])
        zone = Zone.objects.create(
            id=zone_data["id"],
            location=point,
            xp_value=10
        )
        created_zones.append(zone)

    print(f"Created {len(created_zones)} sample zones:")
    for zone in created_zones:
        print(f"  - {zone.id} at ({zone.location.y:.6f}, {zone.location.x:.6f})")

    return created_zones

if __name__ == "__main__":
    create_sample_zones()
    print("\nSample zone data created successfully!")
    print("You can now test the API endpoints with these zones.")

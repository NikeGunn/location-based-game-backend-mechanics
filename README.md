# Location-Based Game Backend

A Django REST Framework backend for a location-based mobile game where users can claim zones, attack others, and compete on leaderboards.

## Features

- **User Authentication**: JWT-based authentication with custom user model
- **Geolocation**: PostGIS-powered zone management with spatial queries
- **Zone System**: Claim zones, 24-hour expiry, grid-based IDs
- **Attack System**: Battle logic with cooldowns and notifications
- **Leaderboards**: Multiple categories (XP, zones owned, level, attacks)
- **Push Notifications**: Firebase integration for real-time alerts
- **Background Tasks**: Celery + Redis for scheduled operations

## Project Structure

```
backend/
├── config/          # Django settings and configuration
├── users/           # User authentication and profiles
├── zones/           # Zone management and check-ins
├── attacks/         # Attack system and battle logic
├── leaderboard/     # Ranking and statistics
├── utils/           # Shared utilities (notifications)
└── tests/           # Test suite
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token
- `GET /api/v1/auth/profile/` - Get user profile

### Zones
- `POST /api/v1/zones/nearby/` - Get nearby zones
- `POST /api/v1/zones/check-in/` - Check in to a zone
- `GET /api/v1/zones/<id>/` - Get zone details
- `GET /api/v1/zones/my-zones/` - Get user's zones

### Attacks
- `POST /api/v1/attacks/attack/` - Attack a zone
- `GET /api/v1/attacks/history/` - Get attack history
- `GET /api/v1/attacks/cooldowns/` - Get active cooldowns
- `GET /api/v1/attacks/stats/` - Get attack statistics

### Leaderboard
- `GET /api/v1/leaderboard/?category=xp` - Get leaderboard
- `GET /api/v1/leaderboard/my-rank/` - Get user's ranks
- `GET /api/v1/leaderboard/stats/` - Get leaderboard stats

## Quick Start

### 1. Environment Setup

```bash
# Clone and setup
git clone <repository>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your configuration
```

### 2. Database Setup

```bash
# Install PostgreSQL with PostGIS
# Windows: Download from https://www.postgresql.org/download/windows/
# Enable PostGIS extension in your database

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 3. Redis Setup

```bash
# Install Redis
# Windows: https://github.com/microsoftarchive/redis/releases
# Or use Docker: docker run -d -p 6379:6379 redis:alpine
```

### 4. Run the Application

```bash
# Start Django server
python manage.py runserver

# In separate terminals, start Celery
celery -A config worker -l info
celery -A config beat -l info
```

### 5. Using Docker (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run migrations in container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Configuration

### Environment Variables

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgis://username:password@localhost:5432/gamedb
REDIS_URL=redis://localhost:6379/0
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json

# Game Configuration
ZONE_CAPTURE_RADIUS_METERS=20
ZONE_EXPIRY_HOURS=24
ATTACK_COOLDOWN_MINUTES=30
```

### Firebase Setup

1. Create a Firebase project
2. Generate a service account key
3. Download the JSON credentials file
4. Set `FIREBASE_CREDENTIALS_PATH` in your environment

## Game Mechanics

### Zone System
- Zones are created dynamically based on grid coordinates
- Users must be within 20 meters to interact with a zone
- Zones expire after 24 hours of ownership
- Each zone has an XP value when claimed

### Attack System
- Users can attack zones owned by others
- Battle outcome based on attacker/defender power + randomness
- 30-minute cooldown between attacks on the same zone
- Push notifications sent for attacks and results

### Leaderboards
- Multiple categories: XP, zones owned, level, successful attacks
- Cached entries updated every 4 hours
- Real-time fallback for uncached data

## Testing

```bash
# Run tests
pytest

# Run specific test file
pytest tests/test_zones.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## Production Deployment

### Using Gunicorn + Nginx

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --workers 3 --bind 0.0.0.0:8000 config.wsgi:application

# Configure Nginx to proxy to Gunicorn
```

### Environment Setup

1. Set `DEBUG=False`
2. Configure proper `ALLOWED_HOSTS`
3. Use production PostgreSQL database
4. Set up Redis for production
5. Configure static file serving
6. Set up SSL certificates

## API Usage Examples

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "player1",
    "email": "player1@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'
```

### Check In to Zone
```bash
curl -X POST http://localhost:8000/api/v1/zones/check-in/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 37.7749,
    "longitude": -122.4194
  }'
```

### Attack Zone
```bash
curl -X POST http://localhost:8000/api/v1/attacks/attack/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "zone_id": "zone_37774_-122419",
    "latitude": 37.7749,
    "longitude": -122.4194
  }'
```

## Contributing

1. Follow Django best practices
2. Use the service layer for business logic
3. Write tests for new features
4. Follow the existing code structure
5. Update documentation for API changes
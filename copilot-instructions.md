# GitHub Copilot Instructions – Django REST Framework Game Backend

## 🧱 Structure Rules
- Follow Django best practices with modular apps:
  - `users/`: user auth, profile, push tokens
  - `zones/`: zone data, check-in, ownership
  - `attacks/`: attack history, battle logic
  - `leaderboard/`: leaderboard views, ranking logic
- Keep views, models, serializers, and permissions separate in each app.

## 🔐 Authentication & Permissions
- Use `djangorestframework-simplejwt` for JWT.
- Restrict all APIs to authenticated users only.
- Users can only modify zones they own.
- Include custom permissions as needed.

## 🌍 Geolocation & Zones
- Use `GeoDjango` and PostGIS with `PointField`.
- Zones are divided using lat/lng grid logic.
- API to fetch nearby zones using `ST_DWithin` or bounding box.
- Zone model contains: owner, timestamp, and coordinates.

## ✅ Check-In Logic
- Validate if user is physically inside zone (within 20 meters).
- If unclaimed, assign zone to user and start timer.
- If claimed by enemy, allow attack if cooldown period is over.
- Use serializers for validation and DRF Views for business logic.

## ⚔️ Attack Logic
- Each attack must be logged.
- User must be physically near zone and not retry within cooldown period.
- Basic logic: random chance + user level + number of zones owned.
- Return battle result and update zone ownership if successful.

## 📈 Leaderboard Logic
- Create API endpoint `/api/leaderboard/` that returns top users based on XP or zone count.
- Recompute scores periodically or on relevant events (check-in, attack, etc).
- Use efficient queries or caching for performance.

## 🕒 Zone Expiry & Tasks
- Use Celery + Redis for scheduled revocation of zones after 24h.
- Set tasks for streaks, expired battles, rewards.
- Run async jobs for zone expiration and leaderboard updates.

## 🔔 Notifications
- Save push tokens on login/register.
- Trigger push on zone attack, loss, defense.
- Use FCM or Expo push with Python SDK (via Celery or direct trigger).

## 📑 API Best Practices
- Version all APIs under `/api/v1/`.
- Use meaningful REST endpoints:
  - `POST /zones/check-in/`
  - `POST /zones/attack/`
  - `GET /zones/nearby/`
- Return consistent JSON response structures with proper status codes.

## 🧪 Testing
- Use `pytest` and `pytest-django`.
- Test zone claiming logic, attack scenarios, and leaderboard ranking logic.
- Test spatial queries and model validations.

## ♻️ Maintainability
- Write reusable serializers and permissions.
- Use service layer for complex business logic.
- Avoid mixing business logic directly inside views.

## 🚀 Deployment
- Use PostgreSQL with PostGIS.
- Use Gunicorn + Nginx in production.
- Use Docker or Render/DigitalOcean for scalable hosting.

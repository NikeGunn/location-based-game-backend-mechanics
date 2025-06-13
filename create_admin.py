from django.contrib.auth import get_user_model

User = get_user_model()

# Create admin user if it doesn't exist
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@gamebackend.com',
        password='admin123'
    )
    print('Admin superuser created successfully!')
    print('Username: admin')
    print('Password: admin123')
else:
    print('Admin user already exists!')

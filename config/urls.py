from django.contrib import admin
from django.urls import path, include
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

class HealthCheckView(APIView):
    """Simple health check endpoint"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        return Response({
            'status': 'healthy',
            'message': 'Django Location-Based Game Backend is running',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0'
        })

class APIRootView(APIView):
    """API Root endpoint showing available endpoints"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        return Response({
            'message': 'Location-Based Game Backend API',
            'version': '1.0.0',
            'endpoints': {
                'authentication': '/api/v1/auth/',
                'zones': '/api/v1/zones/',
                'attacks': '/api/v1/attacks/',
                'leaderboard': '/api/v1/leaderboard/',
                'admin': '/admin/',
            },
            'documentation': {
                'postman_collection': '/postman_collection.json',
                'setup_guide': '/SETUP_COMPLETE.md'
            }
        })

urlpatterns = [
    path('', HealthCheckView.as_view(), name='health_check'),
    path('admin/', admin.site.urls),
    path('api/v1/', APIRootView.as_view(), name='api_root'),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/zones/', include('zones.urls')),
    path('api/v1/attacks/', include('attacks.urls')),
    path('api/v1/leaderboard/', include('leaderboard.urls')),
    path('api/v1/health/', HealthCheckView.as_view(), name='health_check'),
]

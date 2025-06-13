from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ZoneViewSet,
    UserZonesView,
    ZoneCheckInHistoryView
)

# Create router for ViewSet
router = DefaultRouter()
router.register(r'', ZoneViewSet, basename='zones')

urlpatterns = [
    # Include ViewSet URLs (provides list, retrieve, nearby, claim, checkin)
    path('', include(router.urls)),

    # Additional endpoints
    path('my-zones/', UserZonesView.as_view(), name='user_zones'),
    path('checkin-history/', ZoneCheckInHistoryView.as_view(), name='checkin_history'),
]

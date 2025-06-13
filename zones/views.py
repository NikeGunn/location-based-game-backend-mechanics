from rest_framework import status, generics
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from .models import Zone, ZoneCheckIn
from .serializers import (
    ZoneSerializer,
    NearbyZonesSerializer,
    ZoneCheckInSerializer,
    ZoneCheckInResponseSerializer
)
from .permissions import IsZoneOwner
from .services import ZoneService


class ZoneViewSet(ModelViewSet):
    """ViewSet for zone operations"""
    queryset = Zone.objects.select_related('owner')
    serializer_class = ZoneSerializer
    lookup_field = 'id'

    def get_permissions(self):
        """No permissions needed for listing/retrieving zones"""
        return []

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get zones near user's location"""
        try:
            latitude = float(request.query_params.get('latitude'))
            longitude = float(request.query_params.get('longitude'))
            radius = int(request.query_params.get('radius', 1000))

            user_location = Point(longitude, latitude)
            zones = ZoneService.get_nearby_zones(user_location, radius)
            serializer = ZoneSerializer(zones, many=True)

            return Response({
                'zones': serializer.data,
                'count': len(serializer.data)
            })
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid latitude, longitude, or radius'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def claim(self, request, id=None):
        """Claim a zone"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            latitude = float(request.data.get('latitude'))
            longitude = float(request.data.get('longitude'))
            user_location = Point(longitude, latitude)

            zone = get_object_or_404(Zone, id=id)

            # Check if user is within capture radius
            if not ZoneService.validate_user_location(user_location, zone.location):
                return Response(
                    {'error': f'You must be within {settings.ZONE_CAPTURE_RADIUS_METERS}m of the zone'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if zone is already claimed
            if zone.is_claimed and zone.owner != request.user:
                return Response(
                    {'error': 'Zone is already claimed by another player. Use attack to claim it!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if zone.is_claimed and zone.owner == request.user:
                return Response(
                    {'message': 'You already own this zone'},
                    status=status.HTTP_200_OK
                )

            # Claim the zone
            zone.claim(request.user)
            ZoneService.update_user_stats(request.user, zone.xp_value)

            return Response(
                {
                    'message': 'Zone claimed successfully!',
                    'zone': ZoneSerializer(zone).data,
                    'xp_gained': zone.xp_value
                },
                status=status.HTTP_200_OK
            )

        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid latitude or longitude'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def checkin(self, request, id=None):
        """Check into a zone"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            latitude = float(request.data.get('latitude'))
            longitude = float(request.data.get('longitude'))
            user_location = Point(longitude, latitude)

            checkin, message = ZoneService.check_in_to_zone(
                request.user,
                id,
                user_location
            )

            response_serializer = ZoneCheckInResponseSerializer(checkin)
            return Response({
                'checkin': response_serializer.data,
                'message': message
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except (TypeError, AttributeError):
            return Response(
                {'error': 'Invalid latitude or longitude'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserZonesView(APIView):
    """Get zones owned by the current user"""

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        zones = request.user.owned_zones.filter(
            expires_at__gt=timezone.now()
        )
        serializer = ZoneSerializer(zones, many=True)
        return Response({
            'zones': serializer.data,
            'count': len(serializer.data)
        })


class ZoneCheckInHistoryView(APIView):
    """Get user's check-in history"""

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        checkins = ZoneCheckIn.objects.filter(
            user=request.user
        ).select_related('zone', 'zone__owner').order_by('-timestamp')[:50]

        serializer = ZoneCheckInResponseSerializer(checkins, many=True)
        return Response({
            'checkins': serializer.data,
            'count': len(serializer.data)
        })

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import LeaderboardEntry
from .serializers import (
    LeaderboardEntrySerializer,
    UserRankSerializer,
    LeaderboardStatsSerializer,
    DetailedUserStatsSerializer
)
from .services import LeaderboardService

User = get_user_model()


class LeaderboardView(APIView):
    """Get leaderboard for specified category"""

    def get(self, request, category=None):
        # Get category from URL path or query parameter
        if not category:
            category = request.query_params.get('category', 'xp')

        limit = min(int(request.query_params.get('limit', 100)), 100)

        if category not in ['xp', 'zones', 'level', 'attacks']:
            return Response(
                {'error': 'Invalid category. Use: xp, zones, level, or attacks'},
                status=status.HTTP_400_BAD_REQUEST
            )

        entries = LeaderboardService.get_leaderboard(category, limit)

        # If entries are User objects (real-time), convert to leaderboard format
        if entries and isinstance(entries.first(), User):
            data = []
            for rank, user in enumerate(entries, 1):
                if category == 'xp':
                    score = user.xp
                elif category == 'zones':
                    score = user.zones_owned
                elif category == 'level':
                    score = user.level
                elif category == 'attacks':
                    score = user.attacks_made.filter(success=True).count()

                data.append({
                    'rank': rank,
                    'username': user.username,
                    'level': user.level,
                    'score': score,
                    'last_updated': None
                })
        else:
            serializer = LeaderboardEntrySerializer(entries, many=True)
            data = serializer.data

        return Response({
            'category': category,
            'leaderboard': data,
            'count': len(data)
        })


class UserRankView(APIView):
    """Get current user's rank in all categories"""

    def get(self, request):
        categories = ['xp', 'zones', 'level', 'attacks']
        ranks = []

        for category in categories:
            rank_data = LeaderboardService.get_user_rank(request.user, category)
            ranks.append(rank_data)

        return Response({
            'user': request.user.username,
            'ranks': ranks
        })


class UserStatsView(APIView):
    """Get detailed stats for a user"""

    def get(self, request, username=None):
        if username:
            user = get_object_or_404(User, username=username, is_active=True)
        else:
            user = request.user

        serializer = DetailedUserStatsSerializer(user)

        # Get user's ranks
        categories = ['xp', 'zones', 'level', 'attacks']
        ranks = {}
        for category in categories:
            rank_data = LeaderboardService.get_user_rank(user, category)
            ranks[category] = {
                'rank': rank_data['rank'],
                'percentile': rank_data['percentile']
            }

        return Response({
            'user_stats': serializer.data,
            'ranks': ranks
        })


class LeaderboardStatsView(APIView):
    """Get general leaderboard statistics"""

    def get(self, request):
        stats = LeaderboardService.get_leaderboard_stats()
        serializer = LeaderboardStatsSerializer(stats)
        return Response(serializer.data)


class RefreshLeaderboardView(APIView):
    """Manually refresh leaderboard (admin only)"""

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff members can refresh leaderboards'},
                status=status.HTTP_403_FORBIDDEN
            )

        category = request.data.get('category', 'all')

        if category == 'all':
            LeaderboardService.update_leaderboard()
            message = "All leaderboards refreshed successfully"
        elif category in ['xp', 'zones', 'level', 'attacks']:
            LeaderboardService.update_leaderboard(category)
            message = f"{category} leaderboard refreshed successfully"
        else:
            return Response(
                {'error': 'Invalid category'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({'message': message})

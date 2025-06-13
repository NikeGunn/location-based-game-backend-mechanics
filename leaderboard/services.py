from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from zones.models import Zone
from attacks.models import Attack
from .models import LeaderboardEntry, LeaderboardSnapshot

User = get_user_model()


class LeaderboardService:
    """Service class for leaderboard-related business logic"""

    @staticmethod
    def get_leaderboard(category='xp', limit=100):
        """Get leaderboard for specified category"""
        try:
            entries = LeaderboardEntry.objects.filter(
                category=category
            ).select_related('user')[:limit]

            # If no cached entries, generate them
            if not entries.exists():
                LeaderboardService.update_leaderboard(category)
                entries = LeaderboardEntry.objects.filter(
                    category=category
                ).select_related('user')[:limit]

            return entries
        except Exception:
            # Fallback to real-time calculation
            return LeaderboardService.calculate_realtime_leaderboard(category, limit)

    @staticmethod
    def calculate_realtime_leaderboard(category='xp', limit=100):
        """Calculate leaderboard in real-time (fallback method)"""
        if category == 'xp':
            users = User.objects.filter(is_active=True).order_by('-xp')[:limit]
        elif category == 'zones':
            users = User.objects.filter(is_active=True).order_by('-zones_owned')[:limit]
        elif category == 'level':
            users = User.objects.filter(is_active=True).order_by('-level', '-xp')[:limit]
        elif category == 'attacks':
            users = User.objects.filter(is_active=True).annotate(
                successful_attacks=Count('attacks_made', filter=Q(attacks_made__success=True))
            ).order_by('-successful_attacks')[:limit]
        else:
            users = User.objects.filter(is_active=True).order_by('-xp')[:limit]

        return users

    @staticmethod
    def update_leaderboard(category=None):
        """Update cached leaderboard entries"""
        categories = [category] if category else ['xp', 'zones', 'level', 'attacks']

        for cat in categories:
            # Clear existing entries for this category
            LeaderboardEntry.objects.filter(category=cat).delete()

            # Calculate new rankings
            if cat == 'xp':
                users = User.objects.filter(is_active=True).order_by('-xp')
                score_field = 'xp'
            elif cat == 'zones':
                users = User.objects.filter(is_active=True).order_by('-zones_owned')
                score_field = 'zones_owned'
            elif cat == 'level':
                users = User.objects.filter(is_active=True).order_by('-level', '-xp')
                score_field = 'level'
            elif cat == 'attacks':
                users = User.objects.filter(is_active=True).annotate(
                    successful_attacks=Count('attacks_made', filter=Q(attacks_made__success=True))
                ).order_by('-successful_attacks')
                score_field = 'successful_attacks'

            # Create leaderboard entries
            entries_to_create = []
            for rank, user in enumerate(users[:1000], 1):  # Top 1000 users
                if cat == 'attacks':
                    score = user.successful_attacks
                else:
                    score = getattr(user, score_field)

                entries_to_create.append(
                    LeaderboardEntry(
                        user=user,
                        category=cat,
                        score=score,
                        rank=rank
                    )
                )

            LeaderboardEntry.objects.bulk_create(entries_to_create)

    @staticmethod
    def get_user_rank(user, category='xp'):
        """Get user's rank in specified category"""
        try:
            entry = LeaderboardEntry.objects.get(user=user, category=category)
            total_users = LeaderboardEntry.objects.filter(category=category).count()
            percentile = ((total_users - entry.rank) / total_users) * 100

            return {
                'category': category,
                'rank': entry.rank,
                'score': entry.score,
                'total_users': total_users,
                'percentile': round(percentile, 1)
            }
        except LeaderboardEntry.DoesNotExist:
            # Calculate real-time rank
            return LeaderboardService.calculate_realtime_rank(user, category)

    @staticmethod
    def calculate_realtime_rank(user, category='xp'):
        """Calculate user's rank in real-time"""
        if category == 'xp':
            higher_users = User.objects.filter(xp__gt=user.xp, is_active=True).count()
            score = user.xp
        elif category == 'zones':
            higher_users = User.objects.filter(zones_owned__gt=user.zones_owned, is_active=True).count()
            score = user.zones_owned
        elif category == 'level':
            higher_users = User.objects.filter(
                Q(level__gt=user.level) | Q(level=user.level, xp__gt=user.xp),
                is_active=True
            ).count()
            score = user.level
        elif category == 'attacks':
            user_attacks = user.attacks_made.filter(success=True).count()
            higher_users = User.objects.filter(is_active=True).annotate(
                successful_attacks=Count('attacks_made', filter=Q(attacks_made__success=True))
            ).filter(successful_attacks__gt=user_attacks).count()
            score = user_attacks

        total_users = User.objects.filter(is_active=True).count()
        rank = higher_users + 1
        percentile = ((total_users - rank) / total_users) * 100 if total_users > 0 else 0

        return {
            'category': category,
            'rank': rank,
            'score': score,
            'total_users': total_users,
            'percentile': round(percentile, 1)
        }

    @staticmethod
    def get_leaderboard_stats():
        """Get general leaderboard statistics"""
        total_users = User.objects.filter(is_active=True).count()
        total_zones = Zone.objects.filter(owner__isnull=False).count()
        total_attacks = Attack.objects.count()

        # Most active zone (most attacks)
        most_active_zone = Zone.objects.annotate(
            attack_count=Count('attacks')
        ).order_by('-attack_count').first()

        # Top player by XP
        top_player = User.objects.filter(is_active=True).order_by('-xp').first()

        return {
            'total_users': total_users,
            'total_zones': total_zones,
            'total_attacks': total_attacks,
            'most_active_zone': most_active_zone.id if most_active_zone else 'None',
            'top_player': top_player.username if top_player else 'None'
        }

    @staticmethod
    def create_snapshot(category):
        """Create a snapshot of current leaderboard"""
        entries = LeaderboardService.get_leaderboard(category, limit=100)

        data = []
        for entry in entries:
            data.append({
                'rank': entry.rank,
                'username': entry.user.username,
                'score': entry.score,
                'level': entry.user.level
            })

        LeaderboardSnapshot.objects.create(
            category=category,
            data=data
        )

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Attack, AttackCooldown
from .serializers import (
    AttackSerializer,
    AttackResultSerializer,
    AttackHistorySerializer,
    CooldownStatusSerializer
)
from .services import AttackService


class AttackZoneView(APIView):
    """Handle zone attack attempts and get attack history"""

    def post(self, request):
        serializer = AttackSerializer(data=request.data)
        if serializer.is_valid():
            try:
                zone_id = serializer.validated_data['zone_id']
                attacker_location = serializer.validated_data['attacker_location']

                attack = AttackService.execute_attack(
                    request.user,
                    zone_id,
                    attacker_location
                )

                response_serializer = AttackResultSerializer(attack)

                message = "Attack successful! Zone captured!" if attack.success else "Attack failed! Try again later."

                return Response({
                    'attack': response_serializer.data,
                    'message': message
                }, status=status.HTTP_201_CREATED)

            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Get user's attack history"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if getting attacks received vs attacks made
        attack_type = request.query_params.get('type', 'made')

        if attack_type == 'received':
            attacks = Attack.objects.filter(defender=request.user).order_by('-timestamp')[:50]
        else:
            attacks = Attack.objects.filter(attacker=request.user).order_by('-timestamp')[:50]

        serializer = AttackHistorySerializer(
            attacks,
            many=True,
            context={'user': request.user}
        )

        return Response({
            'attacks': serializer.data,
            'count': len(serializer.data)
        })


class AttackHistoryView(APIView):
    """Get user's attack history"""

    def get(self, request):
        attacks = AttackService.get_user_attack_history(request.user)
        serializer = AttackHistorySerializer(
            attacks,
            many=True,
            context={'user': request.user}
        )

        return Response({
            'attacks': serializer.data,
            'count': len(serializer.data)        })


class AttackCooldownView(APIView):
    """Get user's active attack cooldowns"""

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        cooldowns = AttackService.get_user_cooldowns(request.user)
        serializer = CooldownStatusSerializer(cooldowns, many=True)

        return Response({
            'cooldowns': serializer.data,
            'count': len(serializer.data)
        })


class AttackStatsView(APIView):
    """Get user's attack statistics"""

    def get(self, request):
        user = request.user

        # Calculate attack stats
        total_attacks = Attack.objects.filter(attacker=user).count()
        successful_attacks = Attack.objects.filter(attacker=user, success=True).count()
        total_defenses = Attack.objects.filter(defender=user).count()
        successful_defenses = Attack.objects.filter(defender=user, success=False).count()

        attack_success_rate = (successful_attacks / total_attacks * 100) if total_attacks > 0 else 0
        defense_success_rate = (successful_defenses / total_defenses * 100) if total_defenses > 0 else 0

        return Response({
            'total_attacks': total_attacks,
            'successful_attacks': successful_attacks,
            'attack_success_rate': round(attack_success_rate, 1),
            'total_defenses': total_defenses,
            'successful_defenses': successful_defenses,
            'defense_success_rate': round(defense_success_rate, 1),
            'attack_power': user.attack_power
        })

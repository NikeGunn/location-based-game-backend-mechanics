import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
if settings.FIREBASE_CREDENTIALS_PATH and not firebase_admin._apps:
    try:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")


class NotificationService:
    """Service for sending push notifications"""

    @staticmethod
    def send_push_notification(user_token, title, body, data=None):
        """Send a push notification to a specific user"""
        if not user_token:
            return False

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=user_token,
            )

            response = messaging.send(message)
            logger.info(f"Successfully sent message: {response}")
            return True

        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False

    @staticmethod
    def send_zone_attack_notification(defender, zone_id, attacker_username):
        """Send notification when user's zone is attacked"""
        if not defender.push_token:
            return False

        title = "Zone Under Attack!"
        body = f"{attacker_username} is attacking your zone {zone_id}"
        data = {
            'type': 'zone_attack',
            'zone_id': zone_id,
            'attacker': attacker_username
        }

        return NotificationService.send_push_notification(
            defender.push_token, title, body, data
        )

    @staticmethod
    def send_zone_lost_notification(defender, zone_id, attacker_username):
        """Send notification when user loses a zone"""
        if not defender.push_token:
            return False

        title = "Zone Lost!"
        body = f"Your zone {zone_id} was captured by {attacker_username}"
        data = {
            'type': 'zone_lost',
            'zone_id': zone_id,
            'attacker': attacker_username
        }

        return NotificationService.send_push_notification(
            defender.push_token, title, body, data
        )

    @staticmethod
    def send_zone_defended_notification(defender, zone_id, attacker_username):
        """Send notification when user successfully defends a zone"""
        if not defender.push_token:
            return False

        title = "Zone Defended!"
        body = f"You successfully defended zone {zone_id} from {attacker_username}"
        data = {
            'type': 'zone_defended',
            'zone_id': zone_id,
            'attacker': attacker_username
        }

        return NotificationService.send_push_notification(
            defender.push_token, title, body, data
        )


# Celery tasks for async notifications
@shared_task
def send_zone_attack_notification_task(defender_id, zone_id, attacker_username):
    """Async task to send zone attack notification"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        defender = User.objects.get(id=defender_id)
        NotificationService.send_zone_attack_notification(defender, zone_id, attacker_username)
    except User.DoesNotExist:
        logger.error(f"User {defender_id} not found for notification")


@shared_task
def send_zone_result_notification_task(defender_id, zone_id, attacker_username, success):
    """Async task to send zone attack result notification"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        defender = User.objects.get(id=defender_id)
        if success:
            NotificationService.send_zone_lost_notification(defender, zone_id, attacker_username)
        else:
            NotificationService.send_zone_defended_notification(defender, zone_id, attacker_username)
    except User.DoesNotExist:
        logger.error(f"User {defender_id} not found for notification")

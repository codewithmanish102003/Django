from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
import csv
import io
import json
from datetime import timedelta
import requests

from users.models import CustomUser
from chat.models import Conversation, Message, ChatNotification

logger = get_task_logger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_id):
    """Send welcome email to new users."""
    try:
        user = User.objects.get(id=user_id)
        
        subject = 'Welcome to DevConnect!'
        message = render_to_string('tasks/emails/welcome_email.html', {
            'user': user,
            'site_name': 'DevConnect'
        })
        
        send_mail(
            subject=subject,
            message='',
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent successfully to {user.email}")
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        raise
    except Exception as exc:
        logger.error(f"Failed to send welcome email to user {user_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_id, reset_token):
    """Send password reset email."""
    try:
        user = User.objects.get(id=user_id)
        
        subject = 'Password Reset Request - DevConnect'
        message = render_to_string('tasks/emails/password_reset.html', {
            'user': user,
            'reset_token': reset_token,
            'site_name': 'DevConnect'
        })
        
        send_mail(
            subject=subject,
            message='',
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent successfully to {user.email}")
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        raise
    except Exception as exc:
        logger.error(f"Failed to send password reset email to user {user_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_daily_digest(self):
    """Send daily digest email to users."""
    try:
        # Get users who want daily digest (you can add this preference to user model)
        users = User.objects.filter(is_active=True)
        
        # Get today's activity
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get new messages
        new_messages = Message.objects.filter(
            created_at__date=yesterday
        ).count()
        
        # Get new users
        new_users = User.objects.filter(
            date_joined__date=yesterday
        ).count()
        
        # Get active conversations
        active_conversations = Conversation.objects.filter(
            updated_at__date=yesterday
        ).count()
        
        digest_data = {
            'new_messages': new_messages,
            'new_users': new_users,
            'active_conversations': active_conversations,
            'date': yesterday,
        }
        
        # Send digest to each user
        for user in users:
            try:
                subject = f'DevConnect Daily Digest - {yesterday}'
                message = render_to_string('tasks/emails/daily_digest.html', {
                    'user': user,
                    'digest': digest_data,
                    'site_name': 'DevConnect'
                })
                
                send_mail(
                    subject=subject,
                    message='',
                    html_message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                
            except Exception as e:
                logger.error(f"Failed to send digest to {user.email}: {e}")
                continue
        
        logger.info(f"Daily digest sent to {users.count()} users")
        
    except Exception as exc:
        logger.error(f"Failed to send daily digest: {exc}")
        raise self.retry(exc=exc, countdown=300)


@shared_task(bind=True, max_retries=3)
def send_notification_email(self, user_id, notification_type, data):
    """Send notification email to users."""
    try:
        user = User.objects.get(id=user_id)
        
        # Determine email template based on notification type
        if notification_type == 'new_message':
            subject = 'New Message on DevConnect'
            template = 'tasks/emails/new_message.html'
        elif notification_type == 'profile_view':
            subject = 'Someone Viewed Your Profile'
            template = 'tasks/emails/profile_view.html'
        elif notification_type == 'connection_request':
            subject = 'New Connection Request'
            template = 'tasks/emails/connection_request.html'
        else:
            subject = 'DevConnect Notification'
            template = 'tasks/emails/generic_notification.html'
        
        message = render_to_string(template, {
            'user': user,
            'data': data,
            'site_name': 'DevConnect'
        })
        
        send_mail(
            subject=subject,
            message='',
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Notification email sent successfully to {user.email}")
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        raise
    except Exception as exc:
        logger.error(f"Failed to send notification email to user {user_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True)
def generate_user_report(self, user_id, report_type='activity'):
    """Generate user activity report."""
    try:
        user = User.objects.get(id=user_id)
        
        if report_type == 'activity':
            # Generate activity report
            report_data = generate_activity_report(user)
        elif report_type == 'connections':
            # Generate connections report
            report_data = generate_connections_report(user)
        elif report_type == 'messages':
            # Generate messages report
            report_data = generate_messages_report(user)
        else:
            raise ValueError(f"Unknown report type: {report_type}")
        
        # Save report to file or database
        report_filename = f"user_report_{user.username}_{report_type}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # You can save this to a file, database, or cloud storage
        with open(f"reports/{report_filename}", 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"Report generated successfully for user {user.username}")
        
        return report_filename
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        raise
    except Exception as exc:
        logger.error(f"Failed to generate report for user {user_id}: {exc}")
        raise


@shared_task(bind=True)
def generate_system_report(self, report_type='overview'):
    """Generate system-wide report."""
    try:
        if report_type == 'overview':
            # Generate system overview report
            report_data = generate_system_overview_report()
        elif report_type == 'users':
            # Generate users report
            report_data = generate_users_report()
        elif report_type == 'activity':
            # Generate activity report
            report_data = generate_system_activity_report()
        else:
            raise ValueError(f"Unknown report type: {report_type}")
        
        # Save report
        report_filename = f"system_report_{report_type}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(f"reports/{report_filename}", 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"System report generated successfully: {report_filename}")
        
        return report_filename
        
    except Exception as exc:
        logger.error(f"Failed to generate system report: {exc}")
        raise


@shared_task(bind=True)
def cleanup_old_data(self):
    """Clean up old data and logs."""
    try:
        # Clean up old chat notifications (older than 30 days)
        old_notifications = ChatNotification.objects.filter(
            created_at__lt=timezone.now() - timedelta(days=30)
        )
        deleted_notifications = old_notifications.count()
        old_notifications.delete()
        
        # Clean up old messages (older than 1 year)
        old_messages = Message.objects.filter(
            created_at__lt=timezone.now() - timedelta(days=365)
        )
        deleted_messages = old_messages.count()
        old_messages.delete()
        
        # Clean up inactive users (inactive for more than 1 year)
        inactive_users = User.objects.filter(
            last_login__lt=timezone.now() - timedelta(days=365),
            is_active=True
        )
        inactive_users.update(is_active=False)
        
        logger.info(f"Cleanup completed: {deleted_notifications} notifications, {deleted_messages} messages, {inactive_users.count()} users deactivated")
        
    except Exception as exc:
        logger.error(f"Failed to cleanup old data: {exc}")
        raise


@shared_task(bind=True)
def sync_external_data(self):
    """Sync data with external services (GitHub, LinkedIn, etc.)."""
    try:
        # Sync GitHub data for users with GitHub usernames
        users_with_github = User.objects.filter(
            github_username__isnull=False,
            github_username__gt=''
        )
        
        for user in users_with_github:
            try:
                # Fetch GitHub data
                github_data = fetch_github_data(user.github_username)
                
                # Update user profile with GitHub data
                if github_data:
                    user.bio = github_data.get('bio', user.bio)
                    user.website = github_data.get('blog', user.website)
                    user.save()
                    
            except Exception as e:
                logger.error(f"Failed to sync GitHub data for user {user.username}: {e}")
                continue
        
        logger.info(f"External data sync completed for {users_with_github.count()} users")
        
    except Exception as exc:
        logger.error(f"Failed to sync external data: {exc}")
        raise


@shared_task(bind=True)
def send_mass_notification(self, user_ids, notification_data):
    """Send mass notification to multiple users."""
    try:
        users = User.objects.filter(id__in=user_ids, is_active=True)
        
        # Prepare email messages
        email_messages = []
        for user in users:
            try:
                subject = notification_data.get('subject', 'DevConnect Notification')
                message = render_to_string('tasks/emails/mass_notification.html', {
                    'user': user,
                    'notification': notification_data,
                    'site_name': 'DevConnect'
                })
                
                email_messages.append((
                    subject,
                    '',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                ))
                
            except Exception as e:
                logger.error(f"Failed to prepare email for user {user.username}: {e}")
                continue
        
        # Send all emails
        if email_messages:
            send_mass_mail(email_messages, fail_silently=True)
            logger.info(f"Mass notification sent to {len(email_messages)} users")
        
    except Exception as exc:
        logger.error(f"Failed to send mass notification: {exc}")
        raise


# Helper functions for report generation
def generate_activity_report(user):
    """Generate user activity report."""
    # Get user's activity data
    messages_count = Message.objects.filter(sender=user).count()
    conversations_count = Conversation.objects.filter(participants=user).count()
    last_activity = user.last_login
    
    return {
        'user_id': user.id,
        'username': user.username,
        'messages_count': messages_count,
        'conversations_count': conversations_count,
        'last_activity': last_activity,
        'report_generated_at': timezone.now().isoformat()
    }


def generate_connections_report(user):
    """Generate user connections report."""
    # This would be implemented when connections model is added
    return {
        'user_id': user.id,
        'username': user.username,
        'connections_count': 0,
        'report_generated_at': timezone.now().isoformat()
    }


def generate_messages_report(user):
    """Generate user messages report."""
    messages = Message.objects.filter(sender=user).order_by('-created_at')[:100]
    
    return {
        'user_id': user.id,
        'username': user.username,
        'total_messages': messages.count(),
        'recent_messages': [
            {
                'content': msg.content[:100],
                'conversation_id': msg.conversation.id,
                'created_at': msg.created_at.isoformat()
            }
            for msg in messages
        ],
        'report_generated_at': timezone.now().isoformat()
    }


def generate_system_overview_report():
    """Generate system overview report."""
    total_users = User.objects.filter(is_active=True).count()
    total_conversations = Conversation.objects.count()
    total_messages = Message.objects.count()
    
    return {
        'total_users': total_users,
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'report_generated_at': timezone.now().isoformat()
    }


def generate_users_report():
    """Generate users report."""
    users_by_location = User.objects.filter(
        is_active=True,
        location__isnull=False
    ).values('location').annotate(
        count=Count('id')
    ).order_by('-count')[:20]
    
    return {
        'users_by_location': list(users_by_location),
        'total_active_users': User.objects.filter(is_active=True).count(),
        'report_generated_at': timezone.now().isoformat()
    }


def generate_system_activity_report():
    """Generate system activity report."""
    # Get activity for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    new_users = User.objects.filter(
        date_joined__gte=thirty_days_ago
    ).count()
    
    new_messages = Message.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    
    return {
        'new_users_last_30_days': new_users,
        'new_messages_last_30_days': new_messages,
        'report_generated_at': timezone.now().isoformat()
    }


def fetch_github_data(username):
    """Fetch user data from GitHub API."""
    try:
        # GitHub API endpoint
        url = f"https://api.github.com/users/{username}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'bio': data.get('bio'),
                'blog': data.get('blog'),
                'public_repos': data.get('public_repos'),
                'followers': data.get('followers'),
                'following': data.get('following')
            }
        else:
            return None
            
    except requests.RequestException:
        return None

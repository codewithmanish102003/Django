from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Notification(models.Model):
    """Model for user notifications."""
    
    NOTIFICATION_TYPES = [
        ('message', _('New Message')),
        ('profile_view', _('Profile Viewed')),
        ('connection_request', _('Connection Request')),
        ('project_invite', _('Project Invitation')),
        ('job_opportunity', _('Job Opportunity')),
        ('system', _('System Notification')),
        ('achievement', _('Achievement Unlocked')),
        ('reminder', _('Reminder')),
    ]
    
    PRIORITY_LEVELS = [
        ('low', _('Low')),
        ('normal', _('Normal')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='normal')
    
    # Generic foreign key for linking to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Notification metadata
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    # Action data
    action_url = models.URLField(blank=True, null=True)
    action_text = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'notifications'
        
        # Database optimization indexes
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_at']),
            models.Index(fields=['recipient', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} notification for {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.save(update_fields=['is_read'])
    
    def mark_as_sent(self):
        """Mark notification as sent."""
        self.is_sent = True
        self.save(update_fields=['is_sent', 'sent_at'])
    
    @property
    def is_urgent(self):
        """Check if notification is urgent."""
        return self.priority == 'urgent'
    
    @property
    def is_high_priority(self):
        """Check if notification is high priority or urgent."""
        return self.priority in ['high', 'urgent']


class NotificationPreference(models.Model):
    """Model for user notification preferences."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_notifications = models.BooleanField(default=True)
    email_digest = models.BooleanField(default=True)
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', _('Immediate')),
            ('hourly', _('Hourly')),
            ('daily', _('Daily')),
            ('weekly', _('Weekly')),
        ],
        default='daily'
    )
    
    # Push notification preferences
    push_notifications = models.BooleanField(default=True)
    push_sound = models.BooleanField(default=True)
    push_vibration = models.BooleanField(default=True)
    
    # Notification type preferences
    message_notifications = models.BooleanField(default=True)
    profile_view_notifications = models.BooleanField(default=True)
    connection_notifications = models.BooleanField(default=True)
    project_notifications = models.BooleanField(default=True)
    job_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    achievement_notifications = models.BooleanField(default=True)
    reminder_notifications = models.BooleanField(default=True)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='08:00')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"
    
    def should_send_notification(self, notification_type):
        """Check if notification should be sent based on user preferences."""
        if not self.email_notifications:
            return False
        
        # Check specific notification type preference
        if notification_type == 'message' and not self.message_notifications:
            return False
        elif notification_type == 'profile_view' and not self.profile_view_notifications:
            return False
        elif notification_type == 'connection_request' and not self.connection_notifications:
            return False
        elif notification_type == 'project_invite' and not self.project_notifications:
            return False
        elif notification_type == 'job_opportunity' and not self.job_notifications:
            return False
        elif notification_type == 'system' and not self.system_notifications:
            return False
        elif notification_type == 'achievement' and not self.achievement_notifications:
            return False
        elif notification_type == 'reminder' and not self.reminder_notifications:
            return False
        
        return True


class NotificationTemplate(models.Model):
    """Model for notification templates."""
    
    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPES)
    
    # Template content
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    
    # Template variables
    variables = models.JSONField(default=dict, help_text=_('Available template variables'))
    
    # Template metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.notification_type})"
    
    def render(self, context):
        """Render template with context variables."""
        try:
            title = self.title_template.format(**context)
            message = self.message_template.format(**context)
            return title, message
        except KeyError as e:
            # Log missing variables
            return self.title_template, self.message_template


# Signal handlers for automatic notification creation
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    """Create notification preferences for new users."""
    if created:
        NotificationPreference.objects.create(user=instance)


@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    """Send notification when created."""
    if created and not instance.is_sent:
        # Check user preferences
        try:
            preferences = instance.recipient.notification_preferences
            if preferences.should_send_notification(instance.notification_type):
                # Send notification (this would trigger email, push notification, etc.)
                instance.mark_as_sent()
        except NotificationPreference.DoesNotExist:
            # Use default preferences
            instance.mark_as_sent()

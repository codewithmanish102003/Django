from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Conversation(models.Model):
    """Model for chat conversations between users."""
    
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_group_chat = models.BooleanField(default=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-updated_at']
        db_table = 'chat_conversations'
        
        # Database optimization indexes
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['is_group_chat']),
        ]
    
    def __str__(self):
        if self.is_group_chat and self.name:
            return self.name
        elif self.participants.count() == 2:
            return f"Chat between {', '.join([p.username for p in self.participants.all()])}"
        else:
            return f"Group chat with {self.participants.count()} participants"
    
    def get_other_participant(self, user):
        """Get the other participant in a 1-on-1 chat."""
        if self.is_group_chat or self.participants.count() != 2:
            return None
        return self.participants.exclude(id=user.id).first()
    
    def get_unread_count(self, user):
        """Get unread message count for a user."""
        return self.messages.filter(
            sender__in=self.participants.exclude(id=user.id),
            read_by__isnull=True
        ).count()


class Message(models.Model):
    """Model for individual chat messages."""
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(validators=[MinLengthValidator(1)])
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('text', _('Text')),
            ('image', _('Image')),
            ('file', _('File')),
            ('system', _('System Message')),
        ],
        default='text'
    )
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    
    class Meta:
        ordering = ['created_at']
        db_table = 'chat_messages'
        
        # Database optimization indexes
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['message_type']),
            # Removed invalid index on ManyToManyField 'read_by'
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
    
    def mark_as_read(self, user):
        """Mark message as read by a user."""
        self.read_by.add(user)
    
    def is_read_by(self, user):
        """Check if message is read by a user."""
        return self.read_by.filter(id=user.id).exists()


class UserConnection(models.Model):
    """Model for tracking user online status and connections."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='connection')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    connection_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'chat_user_connections'
        indexes = [
            models.Index(fields=['is_online']),
            models.Index(fields=['last_seen']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"
    
    def update_online_status(self, is_online, connection_id=None):
        """Update user's online status."""
        self.is_online = is_online
        if connection_id:
            self.connection_id = connection_id
        self.save()


class ChatNotification(models.Model):
    """Model for chat notifications."""
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_notifications')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'chat_notifications'
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.recipient.username} from {self.message.sender.username}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.save()


# Signal handlers for automatic operations
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


@receiver(post_save, sender=Message)
def create_notifications(sender, instance, created, **kwargs):
    """Create notifications for new messages."""
    if created:
        conversation = instance.conversation
        sender_user = instance.sender
        
        # Create notifications for all participants except sender
        for participant in conversation.participants.exclude(id=sender_user.id):
            ChatNotification.objects.create(
                recipient=participant,
                conversation=conversation,
                message=instance
            )


@receiver(post_save, sender=User)
def create_user_connection(sender, instance, created, **kwargs):
    """Create user connection record for new users."""
    if created:
        UserConnection.objects.create(user=instance)

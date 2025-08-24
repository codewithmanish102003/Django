import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from .models import Conversation, Message, UserConnection, ChatNotification


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat functionality."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Check if user is authenticated
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Check if user is part of the conversation
        if not await self.is_user_in_conversation():
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Update user's online status
        await self.update_user_online_status(True)
        
        # Accept the connection
        await self.accept()
        
        # Send user joined message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'user_id': self.user.id,
                'username': self.user.username,
                'timestamp': timezone.now().isoformat()
            }
        )
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Update user's online status
        await self.update_user_online_status(False)
        
        # Send user left message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_leave',
                'user_id': self.user.id,
                'username': self.user.username,
                'timestamp': timezone.now().isoformat()
            }
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'typing':
                await self.handle_typing_indicator(text_data_json)
            elif message_type == 'read_receipt':
                await self.handle_read_receipt(text_data_json)
            elif message_type == 'typing_stop':
                await self.handle_typing_stop(text_data_json)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
    
    async def handle_chat_message(self, data):
        """Handle incoming chat messages."""
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return
        
        # Save message to database
        message = await self.save_message(message_content)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': message.id,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'sender_avatar': self.get_user_avatar_url(),
                'message': message_content,
                'timestamp': message.created_at.isoformat(),
                'message_type': message.message_type
            }
        )
    
    async def handle_typing_indicator(self, data):
        """Handle typing indicator."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )
    
    async def handle_typing_stop(self, data):
        """Handle typing stop indicator."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing_stop',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )
    
    async def handle_read_receipt(self, data):
        """Handle read receipts."""
        message_id = data.get('message_id')
        if message_id:
            await self.mark_message_as_read(message_id)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': message_id,
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    # WebSocket message handlers
    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'sender_avatar': event['sender_avatar'],
            'message': event['message'],
            'timestamp': event['timestamp'],
            'message_type': event['message_type']
        }))
    
    async def user_join(self, event):
        """Send user join notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))
    
    async def user_leave(self, event):
        """Send user leave notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))
    
    async def user_typing(self, event):
        """Send typing indicator to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'user_id': event['user_id'],
            'username': event['username']
        }))
    
    async def user_typing_stop(self, event):
        """Send typing stop indicator to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'user_typing_stop',
            'user_id': event['user_id'],
            'username': event['username']
        }))
    
    async def read_receipt(self, event):
        """Send read receipt to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))
    
    # Database operations
    @database_sync_to_async
    def is_user_in_conversation(self):
        """Check if user is part of the conversation."""
        try:
            conversation = Conversation.objects.get(id=self.room_name)
            return conversation.participants.filter(id=self.user.id).exists()
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """Save message to database."""
        conversation = Conversation.objects.get(id=self.room_name)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content,
            message_type='text'
        )
        
        # Update conversation timestamp
        conversation.save()
        
        return message
    
    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        """Mark message as read by user."""
        try:
            message = Message.objects.get(id=message_id)
            message.mark_as_read(self.user)
            
            # Mark notification as read
            ChatNotification.objects.filter(
                recipient=self.user,
                message=message
            ).update(is_read=True)
            
        except Message.DoesNotExist:
            pass
    
    @database_sync_to_async
    def update_user_online_status(self, is_online):
        """Update user's online status."""
        connection, created = UserConnection.objects.get_or_create(user=self.user)
        connection.update_online_status(is_online, self.channel_name)
    
    def get_user_avatar_url(self):
        """Get user's avatar URL."""
        if hasattr(self.user, 'avatar') and self.user.avatar:
            return self.user.avatar.url
        return None


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications."""
    
    async def connect(self):
        """Handle WebSocket connection for notifications."""
        self.user = self.scope["user"]
        
        # Check if user is authenticated
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Join user's personal notification group
        self.notification_group_name = f'notifications_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send unread notifications count
        unread_count = await self.get_unread_notifications_count()
        await self.send(text_data=json.dumps({
            'type': 'notifications_count',
            'count': unread_count
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_read':
                await self.handle_mark_read(data)
            elif message_type == 'get_notifications':
                await self.handle_get_notifications(data)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
    
    async def handle_mark_read(self, data):
        """Handle marking notifications as read."""
        notification_id = data.get('notification_id')
        if notification_id:
            await self.mark_notification_as_read(notification_id)
    
    async def handle_get_notifications(self, data):
        """Handle getting user notifications."""
        notifications = await self.get_user_notifications()
        await self.send(text_data=json.dumps({
            'type': 'notifications_list',
            'notifications': notifications
        }))
    
    # Notification handlers
    async def notification_message(self, event):
        """Send notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))
    
    # Database operations
    @database_sync_to_async
    def get_unread_notifications_count(self):
        """Get count of unread notifications."""
        return ChatNotification.objects.filter(
            recipient=self.user,
            is_read=False
        ).count()
    
    @database_sync_to_async
    def get_user_notifications(self):
        """Get user's notifications."""
        notifications = ChatNotification.objects.filter(
            recipient=self.user
        ).select_related('conversation', 'message', 'message__sender')[:20]
        
        return [
            {
                'id': notif.id,
                'conversation_id': notif.conversation.id,
                'message_content': notif.message.content[:100],
                'sender_username': notif.message.sender.username,
                'is_read': notif.is_read,
                'created_at': notif.created_at.isoformat()
            }
            for notif in notifications
        ]
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """Mark notification as read."""
        try:
            notification = ChatNotification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.mark_as_read()
        except ChatNotification.DoesNotExist:
            pass

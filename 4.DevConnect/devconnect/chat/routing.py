from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Chat room WebSocket
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    
    # Notifications WebSocket
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]

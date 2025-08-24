from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    # Chat main pages
    path('', views.chat_home, name='chat_home'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start/<str:username>/', views.start_conversation, name='start_conversation'),
    path('create-group/', views.create_group_chat, name='create_group_chat'),
    path('search/', views.search_conversations, name='search_conversations'),
    path('delete/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
    
    # API endpoints for AJAX requests
    path('api/conversation/<int:conversation_id>/messages/', views.get_conversation_messages, name='get_messages'),
    path('api/conversation/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('api/conversation/<int:conversation_id>/mark-read/', views.mark_conversation_read, name='mark_read'),
    path('api/unread-count/', views.get_unread_count, name='unread_count'),
]

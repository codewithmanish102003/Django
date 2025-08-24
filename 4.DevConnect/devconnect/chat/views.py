from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Max, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView
from users.decorators import login_required as custom_login_required
from users.models import CustomUser

from .models import ChatNotification, Conversation, Message


@custom_login_required
def chat_home(request):
    """Chat home page with conversations list."""
    user = request.user
    
    # Get user's conversations with latest message
    conversations = Conversation.objects.filter(
        participants=user
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time', '-updated_at')
    
    # Get unread counts for each conversation
    for conversation in conversations:
        conversation.unread_count = conversation.get_unread_count(user)
    
    context = {
        'conversations': conversations,
        'user': user,
    }
    return render(request, 'chat/chat_home.html', context)


@custom_login_required
def conversation_detail(request, conversation_id):
    """Detailed view of a conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    # Get messages with pagination
    messages = conversation.messages.select_related('sender').order_by('created_at')
    paginator = Paginator(messages, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Mark messages as read
    unread_messages = conversation.messages.filter(
        sender__in=conversation.participants.exclude(id=request.user.id),
        read_by__isnull=True
    )
    for message in unread_messages:
        message.mark_as_read(request.user)
    
    # Get other participants
    other_participants = conversation.participants.exclude(id=request.user.id)
    
    context = {
        'conversation': conversation,
        'page_obj': page_obj,
        'other_participants': other_participants,
        'user': request.user,
    }
    return render(request, 'chat/conversation_detail.html', context)


@custom_login_required
def start_conversation(request, username):
    """Start a new conversation with a user."""
    other_user = get_object_or_404(CustomUser, username=username, is_active=True)
    
    if other_user == request.user:
        messages.error(request, _("You cannot start a conversation with yourself."))
        return redirect('chat_home')
    
    # Check if conversation already exists
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).filter(
        is_group_chat=False
    ).first()
    
    if existing_conversation:
        return redirect('conversation_detail', conversation_id=existing_conversation.id)
    
    # Create new conversation
    conversation = Conversation.objects.create(is_group_chat=False)
    conversation.participants.add(request.user, other_user)
    
    messages.success(request, _("Conversation started successfully!"))
    return redirect('conversation_detail', conversation_id=conversation.id)


@custom_login_required
def create_group_chat(request):
    """Create a new group chat."""
    if request.method == 'POST':
        chat_name = request.POST.get('chat_name', '').strip()
        participant_ids = request.POST.getlist('participants')
        
        if not chat_name:
            messages.error(request, _("Chat name is required."))
            return redirect('chat_home')
        
        if len(participant_ids) < 2:
            messages.error(request, _("You need at least 2 participants for a group chat."))
            return redirect('chat_home')
        
        # Create group chat
        conversation = Conversation.objects.create(
            is_group_chat=True,
            name=chat_name
        )
        
        # Add participants
        participants = CustomUser.objects.filter(id__in=participant_ids, is_active=True)
        conversation.participants.add(request.user, *participants)
        
        messages.success(request, _("Group chat created successfully!"))
        return redirect('conversation_detail', conversation_id=conversation.id)
    
    # Get available users for group chat
    available_users = CustomUser.objects.filter(
        is_active=True
    ).exclude(
        id=request.user.id
    ).order_by('username')
    
    context = {
        'available_users': available_users,
    }
    return render(request, 'chat/create_group_chat.html', context)


@custom_login_required
def search_conversations(request):
    """Search conversations and users."""
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        # Search in conversations
        conversations = Conversation.objects.filter(
            participants=request.user
        ).filter(
            Q(name__icontains=query) |
            Q(messages__content__icontains=query)
        ).distinct()
        
        # Search for users
        users = CustomUser.objects.filter(
            is_active=True
        ).exclude(
            id=request.user.id
        ).filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )[:10]
        
        results = {
            'conversations': conversations,
            'users': users,
        }
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'chat/search_conversations.html', context)


# API Views for AJAX requests
@login_required
def get_conversation_messages(request, conversation_id):
    """Get messages for a conversation via AJAX."""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    # Get messages with pagination
    page = request.GET.get('page', 1)
    messages = conversation.messages.select_related('sender').order_by('created_at')
    paginator = Paginator(messages, 20)
    
    try:
        page_obj = paginator.page(page)
    except:
        page_obj = paginator.page(1)
    
    # Serialize messages
    message_data = []
    for message in page_obj:
        message_data.append({
            'id': message.id,
            'sender': {
                'id': message.sender.id,
                'username': message.sender.username,
                'avatar': message.sender.avatar.url if message.sender.avatar else None,
            },
            'content': message.content,
            'message_type': message.message_type,
            'created_at': message.created_at.isoformat(),
            'is_edited': message.is_edited,
            'is_read': message.is_read_by(request.user),
        })
    
    return JsonResponse({
        'messages': message_data,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'page_number': page_obj.number,
        'num_pages': page_obj.paginator.num_pages,
    })


@custom_login_required
def send_message(request, conversation_id):
    """Send a message via AJAX."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'error': 'Message content is required'}, status=400)
    
    # Create message
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content,
        message_type='text'
    )
    
    # Update conversation timestamp
    conversation.save()
    
    return JsonResponse({
        'success': True,
        'message': {
            'id': message.id,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
        }
    })


@custom_login_required
def mark_conversation_read(request, conversation_id):
    """Mark all messages in a conversation as read."""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    # Mark unread messages as read
    unread_messages = conversation.messages.filter(
        sender__in=conversation.participants.exclude(id=request.user.id),
        read_by__isnull=True
    )
    
    for message in unread_messages:
        message.mark_as_read(request.user)
    
    return JsonResponse({'success': True})


@custom_login_required
def get_unread_count(request):
    """Get total unread messages count."""
    total_unread = 0
    
    # Get unread count for each conversation
    conversations = Conversation.objects.filter(participants=request.user)
    for conversation in conversations:
        total_unread += conversation.get_unread_count(request.user)
    
    return JsonResponse({'unread_count': total_unread})


@custom_login_required
def delete_conversation(request, conversation_id):
    """Delete a conversation (only for group chats or if user is admin)."""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    # Only allow deletion of group chats or if user is the only participant
    if not conversation.is_group_chat and conversation.participants.count() > 1:
        messages.error(request, _("You cannot delete this conversation."))
        return redirect('chat_home')
    
    if request.method == 'POST':
        conversation.delete()
        messages.success(request, _("Conversation deleted successfully."))
        return redirect('chat_home')
    
    context = {
        'conversation': conversation,
    }
    return render(request, 'chat/delete_conversation.html', context)

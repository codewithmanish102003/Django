from chat.models import Conversation, Message
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count, Max, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView
from users.decorators import login_required as custom_login_required
from users.models import CustomUser


def home(request):
    """Home page view."""
    # Get featured users (users with complete profiles)
    featured_users = CustomUser.objects.filter(
        is_active=True,
        bio__isnull=False,
        bio__gt='',
        location__isnull=False,
        location__gt=''
    ).order_by('-date_joined')[:6]
    
    # Get recent activity
    recent_messages = Message.objects.select_related(
        'sender', 'conversation'
    ).order_by('-created_at')[:5]
    
    # Get platform statistics
    total_users = CustomUser.objects.filter(is_active=True).count()
    total_conversations = Conversation.objects.count()
    total_messages = Message.objects.count()
    
    context = {
        'featured_users': featured_users,
        'recent_messages': recent_messages,
        'stats': {
            'total_users': total_users,
            'total_conversations': total_conversations,
            'total_messages': total_messages,
        }
    }
    
    return render(request, 'profiles/home.html', context)


@custom_login_required
def dashboard(request):
    """User dashboard view."""
    user = request.user
    
    # Get user's recent conversations
    conversations = Conversation.objects.filter(
        participants=user
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')[:5]
    
    # Get unread message counts
    for conversation in conversations:
        conversation.unread_count = conversation.get_unread_count(user)
    
    # Get user's recent activity
    recent_messages = Message.objects.filter(
        sender=user
    ).order_by('-created_at')[:10]
    
    # Get suggested connections (users with similar interests)
    suggested_users = CustomUser.objects.filter(
        is_active=True
    ).exclude(
        id=user.id
    ).exclude(
        id__in=conversations.values_list('participants', flat=True)
    ).filter(
        Q(location=user.location) | 
        Q(github_username__isnull=False) |
        Q(is_available_for_hire=user.is_available_for_hire) |
        Q(is_available_for_projects=user.is_available_for_projects)
    )[:5]
    
    context = {
        'user': user,
        'conversations': conversations,
        'recent_messages': recent_messages,
        'suggested_users': suggested_users,
    }
    
    return render(request, 'profiles/dashboard.html', context)


def user_discovery(request):
    """User discovery page."""
    # Get filter parameters
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    skills = request.GET.get('skills', '')
    available_for = request.GET.get('available_for', '')
    sort_by = request.GET.get('sort', 'recent')
    
    # Base queryset
    users = CustomUser.objects.filter(is_active=True)
    
    # Apply filters
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(bio__icontains=query) |
            Q(github_username__icontains=query)
        )
    
    if location:
        users = users.filter(location__icontains=location)
    
    if available_for == 'hire':
        users = users.filter(is_available_for_hire=True)
    elif available_for == 'projects':
        users = users.filter(is_available_for_projects=True)
    
    # Apply sorting
    if sort_by == 'recent':
        users = users.order_by('-date_joined')
    elif sort_by == 'active':
        users = users.order_by('-last_login')
    elif sort_by == 'name':
        users = users.order_by('first_name', 'last_name')
    elif sort_by == 'location':
        users = users.order_by('location')
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique locations for filter dropdown
    locations = CustomUser.objects.filter(
        is_active=True,
        location__isnull=False,
        location__gt=''
    ).values_list('location', flat=True).distinct().order_by('location')
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'location': location,
        'skills': skills,
        'available_for': available_for,
        'sort_by': sort_by,
        'locations': locations,
    }
    
    return render(request, 'profiles/user_discovery.html', context)


def user_profile(request, username):
    """User profile view."""
    profile_user = get_object_or_404(CustomUser, username=username, is_active=True)
    
    # Check if current user can edit this profile
    can_edit = request.user == profile_user if request.user.is_authenticated else False
    
    # Get user's recent activity
    recent_messages = Message.objects.filter(
        sender=profile_user
    ).order_by('-created_at')[:5]
    
    # Get user's conversations count
    conversations_count = Conversation.objects.filter(
        participants=profile_user
    ).count()
    
    # Get user's messages count
    messages_count = Message.objects.filter(
        sender=profile_user
    ).count()
    
    # Track profile view (if not own profile)
    if request.user.is_authenticated and not can_edit:
        # Here you could create a profile view notification
        pass
    
    context = {
        'profile_user': profile_user,
        'can_edit': can_edit,
        'recent_messages': recent_messages,
        'conversations_count': conversations_count,
        'messages_count': messages_count,
    }
    
    return render(request, 'profiles/user_profile.html', context)


@custom_login_required
def edit_profile(request):
    """Edit user profile view."""
    user = request.user
    
    if request.method == 'POST':
        # Handle profile update
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.bio = request.POST.get('bio', '')
        user.location = request.POST.get('location', '')
        user.github_username = request.POST.get('github_username', '')
        user.linkedin_url = request.POST.get('linkedin_url', '')
        user.portfolio_url = request.POST.get('portfolio_url', '')
        user.website = request.POST.get('website', '')
        user.is_available_for_hire = request.POST.get('is_available_for_hire') == 'on'
        user.is_available_for_projects = request.POST.get('is_available_for_projects') == 'on'
        
        user.save()
        messages.success(request, _('Profile updated successfully!'))
        return redirect('user_profile', username=user.username)
    
    context = {
        'user': user,
    }
    
    return render(request, 'profiles/edit_profile.html', context)


@custom_login_required
def start_chat(request, username):
    """Start a chat with a user."""
    other_user = get_object_or_404(CustomUser, username=username, is_active=True)
    
    if other_user == request.user:
        messages.error(request, _("You cannot start a chat with yourself."))
        return redirect('user_profile', username=username)
    
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
    
    messages.success(request, _("Chat started successfully!"))
    return redirect('conversation_detail', conversation_id=conversation.id)


@custom_login_required
def user_connections(request):
    """User connections page."""
    user = request.user
    
    # Get user's conversations (as a proxy for connections)
    conversations = Conversation.objects.filter(
        participants=user
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    # Get other participants from conversations
    connections = []
    for conversation in conversations:
        if conversation.is_group_chat:
            # For group chats, get all participants
            participants = conversation.participants.exclude(id=user.id)
            connections.extend(participants)
        else:
            # For 1-on-1 chats, get the other participant
            other_participant = conversation.participants.exclude(id=user.id).first()
            if other_participant:
                connections.append(other_participant)
    
    # Remove duplicates
    unique_connections = list({user.id: user for user in connections}.values())
    
    context = {
        'connections': unique_connections,
        'conversations': conversations,
    }
    
    return render(request, 'profiles/user_connections.html', context)


# API Views for AJAX requests
@custom_login_required
@require_http_methods(["POST"])
def update_availability(request, availability_type):
    """Update user availability via AJAX."""
    if availability_type not in ['hire', 'projects']:
        return JsonResponse({'error': 'Invalid availability type'}, status=400)
    
    user = request.user
    
    if availability_type == 'hire':
        user.is_available_for_hire = not user.is_available_for_hire
        user.save()
        return JsonResponse({
            'available': user.is_available_for_hire,
            'message': _('Availability for hire updated successfully!')
        })
    else:
        user.is_available_for_projects = not user.is_available_for_projects
        user.save()
        return JsonResponse({
            'available': user.is_available_for_projects,
            'message': _('Availability for projects updated successfully!')
        })


@custom_login_required
def get_user_suggestions(request):
    """Get user suggestions for search autocomplete."""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    users = CustomUser.objects.filter(
        is_active=True
    ).filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )[:10]
    
    suggestions = [
        {
            'username': user.username,
            'full_name': user.full_name,
            'avatar': user.avatar.url if user.avatar else None,
            'location': user.location,
            'bio': user.bio[:100] if user.bio else '',
        }
        for user in users
    ]
    
    return JsonResponse({'suggestions': suggestions})


@custom_login_required
def get_user_stats(request):
    """Get user statistics via AJAX."""
    user = request.user
    
    # Get user's statistics
    stats = {
        'conversations_count': Conversation.objects.filter(participants=user).count(),
        'messages_count': Message.objects.filter(sender=user).count(),
        'profile_views': 0,  # This would be implemented with a separate model
        'connections_count': 0,  # This would be implemented with a connections model
    }
    
    return JsonResponse(stats)

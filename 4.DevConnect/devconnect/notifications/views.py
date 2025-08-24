from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .models import Notification, NotificationPreference


@login_required
def notification_list(request):
    """Display user's notifications."""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def mark_as_read(request, notification_id):
    """Mark a specific notification as read."""
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        recipient=request.user
    )
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, _('Notification marked as read.'))
    return redirect('notifications:notification_list')


@login_required
def mark_all_as_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, _('All notifications marked as read.'))
    return redirect('notifications:notification_list')


@login_required
def notification_preferences(request):
    """Manage notification preferences."""
    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        # Update preferences based on form data
        preferences.email_notifications = request.POST.get('email_notifications') == 'on'
        preferences.push_notifications = request.POST.get('push_notifications') == 'on'
        preferences.email_frequency = request.POST.get('email_frequency', 'daily')
        
        # Update specific notification type preferences
        preferences.message_notifications = request.POST.get('message_notifications') == 'on'
        preferences.profile_view_notifications = request.POST.get('profile_view_notifications') == 'on'
        preferences.connection_notifications = request.POST.get('connection_notifications') == 'on'
        preferences.project_notifications = request.POST.get('project_notifications') == 'on'
        preferences.job_notifications = request.POST.get('job_notifications') == 'on'
        preferences.system_notifications = request.POST.get('system_notifications') == 'on'
        preferences.achievement_notifications = request.POST.get('achievement_notifications') == 'on'
        preferences.reminder_notifications = request.POST.get('reminder_notifications') == 'on'
        
        # Update quiet hours
        preferences.quiet_hours_enabled = request.POST.get('quiet_hours_enabled') == 'on'
        if preferences.quiet_hours_enabled:
            preferences.quiet_hours_start = request.POST.get('quiet_hours_start', '22:00')
            preferences.quiet_hours_end = request.POST.get('quiet_hours_end', '08:00')
        
        preferences.save()
        messages.success(request, _('Notification preferences updated successfully!'))
        return redirect('notifications:preferences')
    
    context = {
        'preferences': preferences,
    }
    return render(request, 'notifications/preferences.html', context)

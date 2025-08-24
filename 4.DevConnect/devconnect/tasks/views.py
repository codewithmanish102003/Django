from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from .tasks import generate_user_report, generate_system_report


@login_required
def task_status(request):
    """Display task status and history."""
    # This would show task status from Celery
    context = {
        'tasks': [],  # Would be populated with actual task data
    }
    return render(request, 'tasks/task_status.html', context)


@login_required
def trigger_task(request):
    """Trigger a specific task."""
    if request.method == 'POST':
        task_type = request.POST.get('task_type')
        user_id = request.user.id
        
        if task_type == 'user_report':
            # Trigger user report generation
            task = generate_user_report.delay(user_id, 'activity')
            messages.success(request, _('User report generation started!'))
        elif task_type == 'system_report':
            # Trigger system report generation
            task = generate_system_report.delay('overview')
            messages.success(request, _('System report generation started!'))
        else:
            messages.error(request, _('Invalid task type.'))
            return redirect('tasks:task_status')
        
        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'message': _('Task started successfully!')
        })
    
    return redirect('tasks:task_status')

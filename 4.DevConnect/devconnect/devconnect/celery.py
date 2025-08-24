import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devconnect.settings')

app = Celery('devconnect')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery setup."""
    print(f'Request: {self.request!r}')


# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'send-daily-digest': {
        'task': 'tasks.tasks.send_daily_digest',
        'schedule': 86400.0,  # 24 hours
    },
    'cleanup-old-data': {
        'task': 'tasks.tasks.cleanup_old_data',
        'schedule': 604800.0,  # 7 days
    },
    'sync-external-data': {
        'task': 'tasks.tasks.sync_external_data',
        'schedule': 3600.0,  # 1 hour
    },
    'generate-system-report': {
        'task': 'tasks.tasks.generate_system_report',
        'schedule': 2592000.0,  # 30 days
        'args': ('overview',),
    },
}

# Celery configuration
app.conf.update(
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Task execution
    task_always_eager=False,  # Set to True for testing
    task_eager_propagates=True,
    
    # Task routing
    task_routes={
        'tasks.tasks.send_*': {'queue': 'emails'},
        'tasks.tasks.generate_*': {'queue': 'reports'},
        'tasks.tasks.cleanup_*': {'queue': 'maintenance'},
        'tasks.tasks.sync_*': {'queue': 'sync'},
    },
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Result backend configuration
    result_expires=3600,  # 1 hour
    
    # Error handling
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

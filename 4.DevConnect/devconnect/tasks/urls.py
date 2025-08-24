from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Task management endpoints
    path('status/', views.task_status, name='task_status'),
    path('trigger/', views.trigger_task, name='trigger_task'),
]

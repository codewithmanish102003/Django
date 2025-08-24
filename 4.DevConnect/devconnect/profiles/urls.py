from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('discovery/', views.user_discovery, name='user_discovery'),
    
    # User profiles
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/chat/', views.start_chat, name='start_chat'),
    
    # User connections
    path('connections/', views.user_connections, name='user_connections'),
    
    # API endpoints
    path('api/availability/<str:availability_type>/', views.update_availability, name='update_availability'),
    path('api/suggestions/', views.get_user_suggestions, name='user_suggestions'),
    path('api/stats/', views.get_user_stats, name='user_stats'),
]

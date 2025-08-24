from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Profile management
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),
    path('profile/<str:username>/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('settings/', views.profile_settings, name='profile_settings'),
    path('change-password/', views.change_password, name='change_password'),
    
    # User search and discovery
    path('search/', views.user_search, name='user_search'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    
    # API endpoints
    path('toggle-availability/<str:availability_type>/', views.toggle_availability, name='toggle_availability'),
    path('suggestions/', views.user_suggestions, name='user_suggestions'),
]

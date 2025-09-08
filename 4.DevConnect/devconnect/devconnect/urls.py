from django.contrib import admin
from django.urls import path, include
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from profiles.views import profile_list, profile_detail, profile_view, profile_list_view, profile_create_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('core.urls', 'core'), namespace='core')),
    path('api/profiles/', profile_list, name='profile-list'),
    path('api/profiles/<int:pk>/', profile_detail, name='profile-detail'),
    path('profiles/', profile_list_view, name='profile-list-view'),
    path('profiles/create/', profile_create_view, name='profile-create'),
    path('profiles/<int:pk>/', profile_view, name='profile-detail-view'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Auth URLs
    path('accounts/register/', 
         CreateView.as_view(
             template_name='registration/register.html',
             form_class=UserCreationForm,
             success_url=reverse_lazy('core:home')
         ), name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
]
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

from . import views

# Create router for automatic URL generation
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'auth', views.AuthViewSet, basename='auth')

# API URL patterns
urlpatterns = [
    # Router URLs (automatically generated)
    path('', include(router.urls)),
    
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Additional API endpoints
    path('stats/', views.UserStatsView.as_view(), name='user_stats'),
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    
    # API documentation
    path('docs/', include('rest_framework.urls')),
]

# Add router URLs to the main patterns
urlpatterns += router.urls

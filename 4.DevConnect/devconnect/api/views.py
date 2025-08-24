from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import update_last_login
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView
from users.models import CustomUser

from .serializers import (LoginSerializer, PasswordChangeSerializer,
                          PasswordResetConfirmSerializer,
                          PasswordResetSerializer, UserAvailabilitySerializer,
                          UserCreateSerializer, UserProfileSerializer,
                          UserSearchSerializer, UserSerializer,
                          UserSuggestionSerializer, UserUpdateSerializer)


class CustomPageNumberPagination(PageNumberPagination):
    """Custom pagination with configurable page size."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model with full CRUD operations."""
    
    queryset = CustomUser.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'is_available_for_hire', 'is_available_for_projects']
    search_fields = ['username', 'first_name', 'last_name', 'bio', 'github_username']
    ordering_fields = ['username', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    
    def get_queryset(self):
        """Get queryset with optimized database queries."""
        return CustomUser.objects.filter(is_active=True).select_related().prefetch_related()
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'search':
            return UserSearchSerializer
        elif self.action == 'profile':
            return UserProfileSerializer
        elif self.action == 'availability':
            return UserAvailabilitySerializer
        return UserSerializer
    
    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action in ['destroy', 'list']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def search(self, request):
        """Search users with filters."""
        queryset = self.get_queryset()
        
        # Apply additional filters
        query = request.query_params.get('q', '')
        location = request.query_params.get('location', '')
        available_for = request.query_params.get('available_for', '')
        
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(bio__icontains=query) |
                Q(github_username__icontains=query)
            )
        
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        if available_for == 'hire':
            queryset = queryset.filter(is_available_for_hire=True)
        elif available_for == 'projects':
            queryset = queryset.filter(is_available_for_projects=True)
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def profile(self, request, pk=None):
        """Get detailed user profile."""
        user = self.get_object()
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def availability(self, request, pk=None):
        """Update user availability."""
        user = self.get_object()
        
        # Users can only update their own availability
        if request.user != user:
            return Response(
                {'error': _('You can only update your own availability.')},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserAvailabilitySerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def suggestions(self, request):
        """Get user suggestions for search autocomplete."""
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response({'suggestions': []})
        
        users = self.get_queryset().filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )[:10]
        
        serializer = UserSuggestionSerializer(users, many=True, context={'request': request})
        return Response({'suggestions': serializer.data})


class AuthViewSet(viewsets.ViewSet):
    """ViewSet for authentication operations."""
    
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login endpoint."""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            remember_me = serializer.validated_data.get('remember_me', False)
            
            # Try to authenticate with username
            user = authenticate(username=username, password=password)
            
            # If that fails, try with email
            if user is None:
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    pass
            
            if user and user.is_active:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                
                update_last_login(None, user)
                
                return Response({
                    'message': _('Login successful'),
                    'user': UserSerializer(user, context={'request': request}).data
                })
            else:
                return Response({
                    'error': _('Invalid credentials or inactive account')
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """User logout endpoint."""
        logout(request)
        return Response({'message': _('Logout successful')})
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Change user password."""
        user = request.user
        serializer = PasswordChangeSerializer(data=request.data)
        
        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            if not user.check_password(old_password):
                return Response({
                    'error': _('Current password is incorrect')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            
            return Response({'message': _('Password changed successfully')})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Request password reset."""
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email, is_active=True)
                # Here you would typically send a password reset email
                # For now, we'll just return a success message
                return Response({
                    'message': _('If an account with this email exists, a password reset link has been sent.')
                })
            except CustomUser.DoesNotExist:
                # Don't reveal if email exists or not
                return Response({
                    'message': _('If an account with this email exists, a password reset link has been sent.')
                })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def reset_password_confirm(self, request):
        """Confirm password reset with token."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            # Here you would validate the token and reset the password
            # For now, we'll just return a success message
            return Response({
                'message': _('Password reset successful')
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserStatsView(APIView):
    """API view for user statistics."""
    
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def get(self, request):
        """Get user statistics."""
        user = request.user
        
        # Get user's statistics
        stats = {
            'total_users': CustomUser.objects.filter(is_active=True).count(),
            'available_for_hire': CustomUser.objects.filter(is_available_for_hire=True).count(),
            'available_for_projects': CustomUser.objects.filter(is_available_for_projects=True).count(),
            'users_by_location': self._get_users_by_location(),
            'recent_registrations': self._get_recent_registrations(),
        }
        
        return Response(stats)
    
    def _get_users_by_location(self):
        """Get count of users by location."""
        from django.db.models import Count
        return CustomUser.objects.filter(
            is_active=True, 
            location__isnull=False
        ).values('location').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
    
    def _get_recent_registrations(self):
        """Get recent user registrations."""
        recent_users = CustomUser.objects.filter(
            is_active=True
        ).order_by('-date_joined')[:5]
        
        return UserSerializer(recent_users, many=True).data


class HealthCheckView(APIView):
    """Health check endpoint for monitoring."""
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return system health status."""
        from django.db import connection
        
        try:
            # Check database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            return Response({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            return Response({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

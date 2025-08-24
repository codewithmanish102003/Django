from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import CustomUser

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    full_name = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'display_name', 'bio', 'avatar_url', 'date_of_birth', 'github_username',
            'linkedin_url', 'portfolio_url', 'website', 'location',
            'is_available_for_hire', 'is_available_for_projects', 'date_joined',
            'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_avatar_url(self, obj):
        """Get avatar URL or return default."""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'password',
            'password_confirm'
        ]
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(_("Passwords don't match"))
        return attrs
    
    def create(self, validated_data):
        """Create new user with hashed password."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profiles."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'bio', 'avatar', 'date_of_birth',
            'github_username', 'linkedin_url', 'portfolio_url', 'website',
            'location', 'is_available_for_hire', 'is_available_for_projects'
        ]
    
    def validate_github_username(self, value):
        """Validate GitHub username format."""
        if value:
            import re
            if not re.match(r'^[a-zA-Z0-9-]+$', value):
                raise serializers.ValidationError(
                    _('GitHub username can only contain letters, numbers, and hyphens.')
                )
        return value
    
    def validate_linkedin_url(self, value):
        """Validate LinkedIn URL format."""
        if value and 'linkedin.com' not in value:
            raise serializers.ValidationError(_('Please enter a valid LinkedIn URL.'))
        return value


class UserSearchSerializer(serializers.ModelSerializer):
    """Serializer for user search results."""
    
    full_name = serializers.ReadOnlyField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'bio', 'avatar_url', 'location',
            'github_username', 'is_available_for_hire', 'is_available_for_projects'
        ]
    
    def get_avatar_url(self, obj):
        """Get avatar URL or return default."""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None


class UserProfileSerializer(serializers.ModelSerializer):
    """Detailed serializer for user profiles."""
    
    full_name = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    avatar_url = serializers.SerializerMethodField()
    connections_count = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'display_name', 'bio', 'avatar_url', 'date_of_birth', 'github_username',
            'linkedin_url', 'portfolio_url', 'website', 'location',
            'is_available_for_hire', 'is_available_for_projects', 'date_joined',
            'last_login', 'connections_count', 'projects_count'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_avatar_url(self, obj):
        """Get avatar URL or return default."""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None
    
    def get_connections_count(self, obj):
        """Get user's connections count."""
        # This will be implemented when we add connections model
        return 0
    
    def get_projects_count(self, obj):
        """Get user's projects count."""
        # This will be implemented when we add projects model
        return 0


class UserAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for updating user availability."""
    
    class Meta:
        model = User
        fields = ['is_available_for_hire', 'is_available_for_projects']
    
    def update(self, instance, validated_data):
        """Update availability fields."""
        instance.is_available_for_hire = validated_data.get(
            'is_available_for_hire', instance.is_available_for_hire
        )
        instance.is_available_for_projects = validated_data.get(
            'is_available_for_projects', instance.is_available_for_projects
        )
        instance.save()
        return instance


class UserSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for user search suggestions."""
    
    full_name = serializers.ReadOnlyField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['username', 'full_name', 'avatar_url', 'location']
    
    def get_avatar_url(self, obj):
        """Get avatar URL or return default."""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None


# Authentication Serializers
class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(default=False)


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(_("New passwords don't match"))
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(_("New passwords don't match"))
        return attrs

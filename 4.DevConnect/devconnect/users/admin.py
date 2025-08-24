from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser model."""
    
    list_display = ('username', 'email', 'full_name', 'location', 'is_available_for_hire', 
                   'is_available_for_projects', 'email_verified', 'date_joined')
    list_filter = ('is_available_for_hire', 'is_available_for_projects', 'email_verified', 
                  'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'github_username', 'location')
    ordering = ('-date_joined',)
    
    # Fieldsets for editing
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'bio', 'avatar', 'date_of_birth')
        }),
        (_('Developer Profile'), {
            'fields': ('github_username', 'linkedin_url', 'portfolio_url', 'website')
        }),
        (_('Location & Availability'), {
            'fields': ('location', 'is_available_for_hire', 'is_available_for_projects')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Email Verification'), {
            'fields': ('email_verified', 'email_verification_token')
        }),
        (_('Social Login'), {
            'fields': ('social_login_provider', 'social_login_id')
        }),
    )
    
    # Fieldsets for adding new users
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    # Read-only fields
    readonly_fields = ('date_joined', 'last_login', 'email_verification_token')
    
    # Actions
    actions = ['verify_users', 'mark_available_for_hire', 'mark_available_for_projects']
    
    def verify_users(self, request, queryset):
        """Mark selected users as email verified."""
        updated = queryset.update(email_verified=True)
        self.message_user(request, f'{updated} users marked as verified.')
    verify_users.short_description = "Mark selected users as verified"
    
    def mark_available_for_hire(self, request, queryset):
        """Mark selected users as available for hire."""
        updated = queryset.update(is_available_for_hire=True)
        self.message_user(request, f'{updated} users marked as available for hire.')
    mark_available_for_hire.short_description = "Mark selected users as available for hire"
    
    def mark_available_for_projects(self, request, queryset):
        """Mark selected users as available for projects."""
        updated = queryset.update(is_available_for_projects=True)
        self.message_user(request, f'{updated} users marked as available for projects.')
    mark_available_for_projects.short_description = "Mark selected users as available for projects"

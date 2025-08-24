from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Custom User model with additional developer-specific fields."""
    
    # Basic profile fields
    bio = models.TextField(_('Bio'), max_length=500, blank=True)
    avatar = models.ImageField(_('Avatar'), upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(_('Date of Birth'), blank=True, null=True)
    
    # Developer-specific fields
    github_username = models.CharField(_('GitHub Username'), max_length=39, blank=True)
    linkedin_url = models.URLField(_('LinkedIn URL'), blank=True)
    portfolio_url = models.URLField(_('Portfolio URL'), blank=True)
    
    # Location and contact
    location = models.CharField(_('Location'), max_length=100, blank=True)
    website = models.URLField(_('Website'), blank=True)
    
    # Preferences
    is_available_for_hire = models.BooleanField(_('Available for Hire'), default=False)
    is_available_for_projects = models.BooleanField(_('Available for Projects'), default=False)
    
    # Email verification
    email_verified = models.BooleanField(_('Email Verified'), default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    
    # Social login fields
    social_login_provider = models.CharField(max_length=20, blank=True)
    social_login_id = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'users'
        
        # Database optimization indexes
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['github_username']),
            models.Index(fields=['location']),
            models.Index(fields=['is_available_for_hire']),
            models.Index(fields=['is_available_for_projects']),
        ]
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        """Return the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def display_name(self):
        """Return the user's display name."""
        return self.full_name or self.username
    
    def get_absolute_url(self):
        """Return the URL to access a particular user instance."""
        from django.urls import reverse
        return reverse('user_profile', kwargs={'username': self.username})
    
    def save(self, *args, **kwargs):
        """Override save to handle email verification."""
        if not self.pk:  # New user
            self.email_verification_token = self._generate_verification_token()
        super().save(*args, **kwargs)
    
    def _generate_verification_token(self):
        """Generate a random verification token."""
        import secrets
        return secrets.token_urlsafe(32)

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (PasswordChangeForm, UserChangeForm,
                                       UserCreationForm)
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Enter your email')})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter your first name')})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter your last name')})
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Choose a username')
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Enter your password')
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Confirm your password')
        })
    
    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))
        return email


class CustomUserChangeForm(UserChangeForm):
    """Form for updating existing users."""
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'avatar',
                 'date_of_birth', 'github_username', 'linkedin_url', 'portfolio_url',
                 'website', 'location', 'is_available_for_hire', 'is_available_for_projects')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password field read-only
        self.fields['password'].help_text = _(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"../password/\">this form</a>."
        )


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with better styling."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class UserLoginForm(forms.Form):
    """Form for user login."""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Username or Email')
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Password')
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        """Validate login credentials."""
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Try to authenticate with username
            user = authenticate(username=username, password=password)
            
            # If that fails, try with email
            if user is None:
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    pass
            
            if user is None:
                raise forms.ValidationError(_('Invalid username/email or password.'))
            elif not user.is_active:
                raise forms.ValidationError(_('This account is inactive.'))
            
            self.cleaned_data['user'] = user
        
        return self.cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile."""
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'bio', 'avatar', 'date_of_birth',
                 'github_username', 'linkedin_url', 'portfolio_url', 'website',
                 'location', 'is_available_for_hire', 'is_available_for_projects')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.TextInput) or isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.URLInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'date'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
    
    def clean_github_username(self):
        """Validate GitHub username format."""
        github_username = self.cleaned_data.get('github_username')
        if github_username:
            # GitHub usernames can only contain alphanumeric characters and hyphens
            import re
            if not re.match(r'^[a-zA-Z0-9-]+$', github_username):
                raise forms.ValidationError(_('GitHub username can only contain letters, numbers, and hyphens.'))
        return github_username
    
    def clean_linkedin_url(self):
        """Validate LinkedIn URL format."""
        linkedin_url = self.cleaned_data.get('linkedin_url')
        if linkedin_url and 'linkedin.com' not in linkedin_url:
            raise forms.ValidationError(_('Please enter a valid LinkedIn URL.'))
        return linkedin_url

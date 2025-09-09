from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    def save(self, commit=True):
        try:
            # Save the user first
            user = super().save(commit=False)
            user.email = self.cleaned_data['email'].lower()
            user.is_active = True  # Set the user as active by default
            
            # Set first_name and last_name from the name field
            name_parts = self.cleaned_data['name'].strip().split(' ', 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
            
            if commit:
                user.save()
                # The profile will be created by the signal
                
                # Update the profile with the name if it exists
                if hasattr(user, 'profile'):
                    user.profile.name = self.cleaned_data['name']
                    user.profile.email = self.cleaned_data['email'].lower()
                    user.profile.save()
                    
            return user
            
        except Exception as e:
            # Log the error (in production, use proper logging)
            print(f"Error creating user: {str(e)}")
            raise

from django.contrib.auth import get_user_model

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Email or Username',
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'})
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if '@' in username:
            User = get_user_model()
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                pass
        return username

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, UpdateView

from .forms import (CustomPasswordChangeForm, CustomUserCreationForm,
                    ProfileUpdateForm, UserLoginForm)
from .models import CustomUser


class UserRegistrationView(CreateView):
    """View for user registration."""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(self.request, _('Account created successfully! Please log in.'))
        return response


class CustomLoginView(LoginView):
    """Custom login view with remember me functionality."""
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('profiles:home')
    
    def get_success_url(self):
        """Redirect to next parameter or default success URL."""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return self.success_url


class CustomLogoutView(LogoutView):
    """Custom logout view."""
    next_page = reverse_lazy('profiles:home')
    
    def dispatch(self, request, *args, **kwargs):
        """Handle logout and show message."""
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, _('You have been logged out successfully.'))
        return response


class UserProfileView(DetailView):
    """View for displaying user profiles."""
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        """Get user by username or return 404."""
        username = self.kwargs.get('username')
        return get_object_or_404(CustomUser, username=username)
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        profile_user = context['profile_user']
        
        # Add user's recent activity, projects, etc.
        context['is_own_profile'] = self.request.user == profile_user
        context['can_edit'] = self.request.user == profile_user
        
        return context


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating user profiles."""
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'users/profile_edit.html'
    
    def test_func(self):
        """Ensure user can only edit their own profile."""
        profile_user = self.get_object()
        return self.request.user == profile_user
    
    def get_object(self):
        """Get the current user's profile."""
        return self.request.user
    
    def get_success_url(self):
        """Redirect to user's profile after successful update."""
        return reverse_lazy('profiles:user_profile', kwargs={'username': self.request.user.username})
    
    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(self.request, _('Profile updated successfully!'))
        return response


@login_required
def profile_settings(request):
    """View for profile settings page."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profile updated successfully!'))
            return redirect('users:profile_settings')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'users/profile_settings.html', context)


@login_required
def change_password(request):
    """View for changing user password."""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Password changed successfully!'))
            return redirect('users:profile_settings')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'users/change_password.html', context)


def user_search(request):
    """View for searching users."""
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    skills = request.GET.get('skills', '')
    available_for = request.GET.get('available_for', '')
    
    users = CustomUser.objects.filter(is_active=True)
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(bio__icontains=query) |
            Q(github_username__icontains=query)
        )
    
    if location:
        users = users.filter(location__icontains=location)
    
    if available_for == 'hire':
        users = users.filter(is_available_for_hire=True)
    elif available_for == 'projects':
        users = users.filter(is_available_for_projects=True)
    
    # Order by most recent activity
    users = users.order_by('-last_login')
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'location': location,
        'skills': skills,
        'available_for': available_for,
    }
    return render(request, 'users/user_search.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_availability(request, availability_type):
    """Toggle user availability for hire or projects."""
    if availability_type not in ['hire', 'projects']:
        return JsonResponse({'error': 'Invalid availability type'}, status=400)
    
    user = request.user
    
    if availability_type == 'hire':
        user.is_available_for_hire = not user.is_available_for_hire
        user.save()
        return JsonResponse({
            'available': user.is_available_for_hire,
            'message': _('Availability for hire updated successfully!')
        })
    else:
        user.is_available_for_projects = not user.is_available_for_projects
        user.save()
        return JsonResponse({
            'available': user.is_available_for_projects,
            'message': _('Availability for projects updated successfully!')
        })


@login_required
def user_dashboard(request):
    """User dashboard view."""
    user = request.user
    
    context = {
        'user': user,
        'recent_activity': [],  # Will be populated with user activity
        'connections_count': 0,  # Will be populated with connection count
        'projects_count': 0,     # Will be populated with project count
    }
    
    return render(request, 'users/dashboard.html', context)


# API Views for AJAX requests
@login_required
@require_http_methods(["GET"])
def user_suggestions(request):
    """Get user suggestions for search autocomplete."""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    users = CustomUser.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )[:10]
    
    suggestions = [
        {
            'username': user.username,
            'full_name': user.full_name,
            'avatar': user.avatar.url if user.avatar else None,
            'location': user.location,
        }
        for user in users
    ]
    
    return JsonResponse({'suggestions': suggestions})

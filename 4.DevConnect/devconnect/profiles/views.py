from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy
from rest_framework.decorators import (
    api_view, 
    permission_classes, 
    throttle_classes
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializer import UserProfileSerializer
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .permissions import IsOwnerOrReadOnly
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def profile_list(request):
    if request.method == 'GET':
        profiles = UserProfile.objects.all()
        serializer = UserProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def profile_detail(request, pk):
    try:
        profile = UserProfile.objects.get(pk=pk)
    except UserProfile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
def profile_list_view(request):
    profiles = UserProfile.objects.select_related('user').all()
    return render(request, 'profiles/profile_list.html', {'profiles': profiles})
def profile_create_view(request):
    if request.method == 'POST':
        form_data = request.POST.dict()
        form_data['user'] = request.user.id
        serializer = UserProfileSerializer(data=form_data)
        if serializer.is_valid():
            serializer.save()
            return redirect('profile-detail-view', pk=serializer.data['id'])
    else:
        return render(request, 'profiles/profile_form.html')

def profile_view(request, pk):
    profile = UserProfile.objects.select_related('user').get(pk=pk)
    return render(request, 'profiles/profile_detail.html', {'profile': profile})

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'profiles/register.html'
    success_url = reverse_lazy('profile-list-view')

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else str(self.success_url)

    def form_valid(self, form):
        try:
            # Save the user first
            response = super().form_valid(form)
            
            # Authenticate the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(
                username=username,
                password=password
            )
            
            if user is not None:
                login(self.request, user)
                messages.success(self.request, 'Registration successful! Welcome to DevConnect.')
            
            return response
            
        except Exception as e:
            # Log the error (in production, you'd use proper logging)
            print(f"Error during registration: {str(e)}")
            messages.error(self.request, 'An error occurred during registration. Please try again.')
            return self.form_invalid(form)

class LoginView(FormView):
    form_class = CustomAuthenticationForm
    template_name = 'profiles/login.html'
    success_url = reverse_lazy('profile-list-view')

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else str(self.success_url)

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        # Try to authenticate with the provided credentials
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(self.request, user)
                messages.success(self.request, f'Welcome back, {user.get_short_name() or user.username}!')
                return super().form_valid(form)
            else:
                messages.error(self.request, 'This account is inactive.')
        else:
            messages.error(self.request, 'Invalid username/email or password.')
            
        return self.form_invalid(form)

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('core:home')

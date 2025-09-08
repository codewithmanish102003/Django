from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .models import UserProfile
from .serializer import UserProfileSerializer
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
            serializer.save()
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

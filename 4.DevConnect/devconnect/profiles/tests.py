from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient, force_authenticate
from rest_framework import status
from .models import UserProfile
from .serializer import UserProfileSerializer
from .views import profile_list, profile_detail
import tempfile
import os
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class UserProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test data that will be shared by all test methods
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        # Get the profile that was automatically created by the signal
        cls.profile = UserProfile.objects.get(user=cls.user)
        # Update the profile with test data
        cls.profile.bio = 'Test bio'
        cls.profile.skills = 'Python, Django, Testing'
        cls.profile.save()

    def test_user_profile_creation(self):
        """Test that a user profile is created with the correct fields"""
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.bio, 'Test bio')
        self.assertEqual(self.profile.skills, 'Python, Django, Testing')
        self.assertEqual(self.profile.email, 'test@example.com')

    def test_get_skills_list(self):
        """Test the get_skills_list property"""
        skills_list = self.profile.get_skills_list
        self.assertEqual(len(skills_list), 3)
        self.assertIn('Python', skills_list)
        self.assertIn('Django', skills_list)
        self.assertIn('Testing', skills_list)

    def test_user_profile_str_method(self):
        """Test the string representation of UserProfile"""
        self.assertEqual(str(self.profile), "Test User's Profile")

    def test_profile_created_on_user_creation(self):
        """Test that a profile is automatically created when a user is created"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        self.assertTrue(hasattr(new_user, 'profile'))
        self.assertEqual(new_user.profile.email, 'new@example.com')


class UserProfileAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Get the profile that was automatically created by the signal
        cls.profile = UserProfile.objects.get(user=cls.user)
        # Update the profile with test data
        cls.profile.bio = 'Test bio'
        cls.profile.skills = 'Python, Django'
        cls.profile.save()
    
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse('profile-list')
        self.detail_url = reverse('profile-detail', kwargs={'pk': self.profile.pk})

    def test_get_profile_list_authenticated(self):
        """Test retrieving a list of profiles"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['bio'], 'Test bio')

    def test_create_profile_authenticated(self):
        """Test creating a new profile"""
        data = {
            'bio': 'New bio',
            'skills': 'JavaScript, React',
            'email': 'new@example.com'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserProfile.objects.count(), 2)
        self.assertEqual(UserProfile.objects.get(pk=2).bio, 'New bio')

    def test_update_profile_owner(self):
        """Test updating a profile by the owner"""
        data = {'bio': 'Updated bio'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated bio')

    def test_delete_profile(self):
        """Test deleting a profile"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UserProfile.objects.count(), 0)


class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Get the profile that was automatically created by the signal
        cls.profile = UserProfile.objects.get(user=cls.user)
        # Update the profile with test data
        cls.profile.bio = 'Test bio'
        cls.profile.skills = 'Python, Django'
        cls.profile.save()
    
    def setUp(self):
        self.client = Client()

    def test_profile_list_view(self):
        """Test the profile list view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile-list-view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test bio')

    def test_profile_detail_view(self):
        """Test the profile detail view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile-detail-view', kwargs={'pk': self.profile.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test bio')

    def test_register_view(self):
        """Test user registration"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view(self):
        """Test user login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success

    def test_logout_view(self):
        """Test user logout"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect on success


class SerializerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Get the profile that was automatically created by the signal
        cls.profile = UserProfile.objects.get(user=cls.user)
        cls.profile_data = {
            'user': cls.user.id,
            'bio': 'Test bio',
            'skills': 'Python, Django',
            'email': 'test@example.com'
        }

    def test_user_profile_serializer(self):
        """Test the UserProfileSerializer"""
        serializer = UserProfileSerializer(data=self.profile_data)
        self.assertTrue(serializer.is_valid())
        profile = serializer.save()
        self.assertEqual(profile.bio, 'Test bio')
        self.assertEqual(profile.skills, 'Python, Django')

    def test_user_profile_serializer_update(self):
        """Test updating a profile with the serializer"""
        # Update the existing profile instead of creating a new one
        serializer = UserProfileSerializer(instance=self.profile, data={
            'bio': 'Updated bio',
            'skills': 'Updated skills',
            'email': 'updated@example.com'
        }, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()
        self.assertEqual(updated_profile.bio, 'Updated bio')
        self.assertEqual(updated_profile.skills, 'Updated skills')
        self.assertEqual(updated_profile.email, 'updated@example.com')

"""
Tests for user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Test the public user API (no authentication required)."""

    def setUp(self):
        """Create a client and a user."""
        self.client = APIClient()


    def test_create_user_success(self):
        """Test creating a new user with valid payload."""
        payload = {
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exist_error(self):
        """Test creating a user with an already registered email."""
        payload = {
            'email': 'test@example.com',
            'password': 'new_password',
            'name': 'Test User'
        }
        create_user(**payload)   # Create a user with the same email
        res = self.client.post(CREATE_USER_URL, payload)
    
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test creating a user with a password less than 5 characters."""
        payload = {
            'email': 'test2@example.com',
            'password': 'pw',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generating a token for a user."""
        user_details = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_with_invalid_credentials(self):
        """Test generating a token with invalid credentials."""
        
        create_user(email='test@example.com', password='goodpass')
        
        payload = {
            'email': 'test@example.com',
            'password': 'badpass'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test generating a token with a blank password."""
                
        payload = {
            'email': 'test@example.com',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test retrieving user with unauthorized access."""
        
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test the private user API (authentication required)."""

    def setUp(self):
        """Create a client and a user for authenticated tests."""
        self.user = create_user(
            email='test@example.com',
            password='password123',
            name='Test User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def test_retrieve_user_profile_success(self):
        """Test retrieving the user profile with authenticated access."""
        
        res = self.client.get(ME_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })
    
    def test_post_me_not_allowed(self):
        """Test post not allowed for the me endpoint."""
        
        res = self.client.post(ME_URL, {})
        
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile_success(self):
        """Test updating the user profile with authenticated access."""
        
        payload = {
            'name': 'Updated name',
            'password': 'newpassword123'
        }
        res = self.client.patch(ME_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password, payload['password'])

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

CREATE_USER_URL = reverse('users:create')
TOKEN_URL = reverse('users:token')


def create_user(**kwargs):
    return User.objects.create_user(**kwargs)


class PublicUserAPITests(TestCase):
    """Test the user API (public)"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.payload = {
            'email': 'test@test.com',
            'password': 'pass1',  # make sure min password length is allowed
            'name': 'Test Name'
        }

    def test_create_valid_user_success(self):
        """Test creating user with valid info is successful"""

        response = self.client.post(CREATE_USER_URL, data=self.payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(**response.data)
        self.assertTrue(user.check_password(self.payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        """Test creating a user that already exists"""

        create_user(**self.payload)
        response = self.client.post(CREATE_USER_URL, data=self.payload)
        self.assertEqual(len(response.data), 1)
        self.assertContains(response,
                            'email',
                            status_code=status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test password should be more than 5 chars"""

        self.payload['password'] = 'pass'
        response = self.client.post(CREATE_USER_URL, data=self.payload)
        self.assertEqual(len(response.data), 1)
        self.assertContains(response,
                            'password',
                            status_code=status.HTTP_400_BAD_REQUEST)
        user_exists = User.objects.filter(email=self.payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""

        create_user(**self.payload)

        payload = {
            'email': self.payload['email'],
            'password': self.payload['password'],
        }

        response = self.client.post(TOKEN_URL, payload)
        self.assertContains(response, 'token')

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""

        create_user(**self.payload)

        payload = {
            'email': self.payload['email'],
            'password': 'wrong_password',
        }

        self.assertTokenNotCreated(payload)

    def test_create_token_missing_field(self):
        """Test that email and password are required for token"""

        payload = {
            'email': self.payload['email'],
            'password': '',
        }

        self.assertTokenNotCreated(payload)

    def test_create_token_no_user(self):
        """Test that token is not created if user does not exists"""

        payload = {
            'email': self.payload['email'],
            'password': self.payload['password'],
        }

        self.assertTokenNotCreated(payload)

    def assertTokenNotCreated(self, payload):
        """Assert that the token won't be created for the given payload"""

        response = self.client.post(TOKEN_URL, payload)
        self.assertNotContains(response,
                               'token',
                               status_code=status.HTTP_400_BAD_REQUEST)


class PrivateUserAPITests(TestCase):
    """Test the user API (private)"""
    pass

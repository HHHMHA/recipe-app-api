from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

CREATE_USER_URL = reverse('users:create')
TOKEN_URL = reverse('users:token')
USER_DETAIL_URL = reverse('users:detail')


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

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""

        response = self.client.get(USER_DETAIL_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def assertTokenNotCreated(self, payload):
        """Assert that the token won't be created for the given payload"""

        response = self.client.post(TOKEN_URL, payload)
        self.assertNotContains(response,
                               'token',
                               status_code=status.HTTP_400_BAD_REQUEST)


class PrivateUserAPITests(TestCase):
    """Test the user API that requires authentication (private)"""

    def setUp(self) -> None:
        self.user = create_user(
            email='test@test.com',
            password='pass1234',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""

        response = self.client.get(USER_DETAIL_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_detail_now_allowed(self):
        """Test that post requests are not allowed to the user detail api"""

        response = self.client.post(USER_DETAIL_URL, {})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""

        payload = {
            'name': 'new name',
            'password': 'new password',
        }

        response = self.client.patch(USER_DETAIL_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))

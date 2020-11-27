from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class ModelTests(TestCase):
    def test_create_user_with_email(self):
        """Test creating a new user with an email"""

        email = "test@gmail.com"
        password = "test1234"

        user = User.objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(User.objects.count(), 1)

    def test_new_user_email_normalized(self):
        """Test the email of a new user is normalized"""

        email = "test@GMAIL.COM"
        user = User.objects.create_user(email=email, password="test1234")
        self.assertEqual(user.email, email.lower())

    def test_create_user_with_invalid_email(self):
        """Test creating user with no email raises ValueError"""

        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="test1234")

        self.assertEqual(User.objects.count(), 0)

    def test_create_superuser(self):
        """Test creating a superuser"""

        user = User.objects.create_superuser('test@gmail.com', 'test1234')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

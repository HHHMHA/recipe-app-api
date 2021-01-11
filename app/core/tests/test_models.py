from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

User = get_user_model()


def sample_user(email='test@test.com', password='pass1234'):
    """Create a sample user"""

    return User.objects.create_user(email, password)


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

    def test_tag_str(self):
        """Test the tag string representation"""

        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""

        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber',
        )

        self.assertEqual(str(ingredient), ingredient.name)

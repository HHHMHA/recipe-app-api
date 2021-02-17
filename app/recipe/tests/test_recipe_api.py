from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer

User = get_user_model()

RECIPES_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **kwargs):
    """Create and return a sample recipe"""
    params = {
        'title': 'sample recipe',
        'time_minutes': 5,
        'price': 5.0
    }
    params.update(kwargs)

    return Recipe.objects.get_or_create(user=user, **params)


class PublicRecipeApiTest(TestCase):
    """Test unauthenticated recipe api access"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""

        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test the private recipe api"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(
            email='test@test.com',
            password='test1234'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""

        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        recipes_data = RecipeSerializer(recipes, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, recipes_data)

    def test_recipe_are_limited_to_user(self):
        """Test retrieving recipes for user"""

        other_user = User.objects.create_user(
            "other@test.com",
            "pass1234"
        )

        sample_recipe(user=self.user)
        sample_recipe(user=other_user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        recipes_data = RecipeSerializer(recipes, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, recipes_data)

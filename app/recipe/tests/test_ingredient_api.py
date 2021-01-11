from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")

User = get_user_model()


class PublicIngredientsAPITests(TestCase):
    """Test the publicly available ingredient API"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """Test tht login is required to access the endpoint"""

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITest(TestCase):
    """Test the private ingredients api"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@test.com',
            password='pass1234',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Test retrieving a list of ingredients"""

        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        response = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for the authenticated user are returned"""

        other_user = User.objects.create_user(
            email='test2@test.com',
            password='pass1234',
        )

        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=other_user, name='Salt')

        response = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.filter(user=self.user)\
                                        .order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_ingredient_successful(self):
        """Test create a new ingredient"""

        payload = {
            'name': 'Cabbage'
        }

        response = self.client.post(INGREDIENTS_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient fails"""

        payload = {'name': ''}

        response = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

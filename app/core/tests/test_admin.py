from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()


class AdminSiteTests(TestCase):

    def setUp(self) -> None:
        self.admin_user = User.objects.create_superuser(
            email='admin@admin.com',
            password='pass1234'
        )
        self.client.force_login(self.admin_user)
        self.user = User.objects.create_user(
            email='user@user.com',
            password='pass1234',
            name='Full Name'
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""

        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

        self.assertContains(res, self.admin_user.name)
        self.assertContains(res, self.admin_user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""

        url = reverse('admin:core_user_change', args=(self.user.id, ))
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_user_page(self):
        """Test that the create user page works"""

        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

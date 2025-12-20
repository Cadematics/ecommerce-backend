from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileTests(APITestCase):
    def setUp(self):
        # Create and authenticate a user
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.force_authenticate(user=self.user)

        # URLs
        self.me_url = reverse('user-detail')

    def test_user_can_view_own_profile(self):
        """
        Ensure an authenticated user can view their own profile.
        """
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_user_can_update_profile(self):
        """
        Ensure an authenticated user can update their own profile.
        """
        update_data = {'first_name': 'Test', 'last_name': 'User'}
        response = self.client.put(self.me_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')

    def test_unauthenticated_access_is_rejected(self):
        """
        Ensure unauthenticated users cannot access profile information.
        """
        self.client.force_authenticate(user=None)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

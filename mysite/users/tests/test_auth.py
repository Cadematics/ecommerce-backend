from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('user-register')
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
            'password2': 'testpassword'
        }

    def test_successful_user_registration(self):
        """
        Ensure a new user can be registered successfully.
        """
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_duplicate_email_rejection(self):
        """
        Ensure registration with a duplicate email is rejected.
        """
        # Create a user first
        self.client.post(self.register_url, self.user_data, format='json')
        # Try to register again with the same email
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_login(self):
        """
        Ensure a registered user can log in and receive tokens.
        """
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'email': 'test@example.com', 'password': 'testpassword'}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_access_protected_endpoint_with_token(self):
        """
        Ensure a protected endpoint can be accessed with a valid token.
        """
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'email': 'test@example.com', 'password': 'testpassword'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['access']

        protected_url = reverse('user-detail')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reject_protected_endpoint_without_token(self):
        """
        Ensure a protected endpoint rejects access without a token.
        """
        protected_url = reverse('user-detail')
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        """
        Ensure a refresh token can be used to obtain a new access token.
        """
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'email': 'test@example.com', 'password': 'testpassword'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']

        response = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
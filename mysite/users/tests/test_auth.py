from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class AuthTests(APITestCase):
    def setUp(self):
        # URLs for auth endpoints
        self.register_url = reverse('user-register')
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('user-profile')

        # Test user data
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'strong-password-123',
            'password2': 'strong-password-123'
        }

    def test_user_registration_success(self):
        """
        Ensure a new user can be registered successfully.
        """
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_user_registration_duplicate_email(self):
        """
        Ensure registration fails if the email already exists.
        """
        # Create the first user
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Attempt to register again with the same email
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_user_login_success(self):
        """
        Ensure a registered user can log in and receive access and refresh tokens.
        """
        # Register user first
        self.client.post(self.register_url, self.user_data, format='json')

        login_data = {'username': 'testuser', 'password': 'strong-password-123'}
        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_access_protected_endpoint_with_token(self):
        """
        Ensure a protected endpoint can be accessed with a valid access token.
        """
        # Register and log in the user
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'username': 'testuser', 'password': 'strong-password-123'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['access']

        # Access a protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_protected_endpoint_without_token(self):
        """
        Ensure a protected endpoint cannot be accessed without a token.
        """
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_refresh_token_returns_new_access_token(self):
        """
        Ensure posting a valid refresh token returns a new access token.
        """
        # Register and log in
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'username': 'testuser', 'password': 'strong-password-123'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']

        # Refresh the token
        response = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_user_logout(self):
        """
        Ensure a user can log out by blacklisting the refresh token.
        """
        # Register and log in
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'username': 'testuser', 'password': 'strong-password-123'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']

        # Set auth header for logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Logout
        response = self.client.post(self.logout_url, {'refresh_token': refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Try to use the blacklisted refresh token
        refresh_response = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

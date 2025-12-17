from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ..models import UserProfile, Address

class UserProfileTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123', email='user1@example.com')
        self.user2 = User.objects.create_user(username='user2', password='password123')

        self.profile1 = UserProfile.objects.get(user=self.user1)
        self.profile2 = UserProfile.objects.get(user=self.user2)

        self.address1 = Address.objects.create(
            profile=self.profile1, 
            address_line_1='123 Main St', 
            city='Anytown', 
            state='CA', 
            postal_code='12345',
            country='USA'
        )

        self.profile_url = reverse('user-profile')
        self.addresses_url = reverse('address-list-create')
        self.address_detail_url = reverse('address-detail', kwargs={'id': self.address1.id})

        self.client.force_authenticate(user=self.user1)

    def test_user_can_view_own_profile(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user1.username)

    def test_user_can_update_own_profile(self):
        update_data = {'email': 'newemail@example.com'}
        response = self.client.patch(self.profile_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, 'newemail@example.com')

    def test_unauthenticated_user_cannot_access_profile(self):
        self.client.logout()
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_list_own_addresses(self):
        response = self.client.get(self.addresses_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['address_line_1'], '123 Main St')

    def test_user_can_create_address(self):
        new_address_data = {
            'address_line_1': '456 Oak Ave',
            'city': 'Otherville',
            'state': 'NY',
            'postal_code': '54321',
            'country': 'USA',
        }
        response = self.client.post(self.addresses_url, new_address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.profile1.addresses.count(), 2)

    def test_user_cannot_access_another_users_address(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.address_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_own_address(self):
        update_data = {'address_line_1': '123 Main Street Updated'}
        response = self.client.patch(self.address_detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.address1.refresh_from_db()
        self.assertEqual(self.address1.address_line_1, '123 Main Street Updated')

    def test_user_can_delete_own_address(self):
        response = self.client.delete(self.address_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Address.objects.filter(pk=self.address1.id).exists())

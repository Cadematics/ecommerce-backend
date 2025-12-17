import stripe
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from unittest.mock import patch
from orders.models import Order
from users.models import UserProfile, Address

# Mock the Stripe API client
@patch('stripe.PaymentIntent.create')
class PaymentTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.user = User.objects.create_user(username='paymentuser', password='password123')
        self.client.force_authenticate(user=self.user)

        # Create an associated profile and address
        self.profile = UserProfile.objects.create(user=self.user)
        self.address = Address.objects.create(
            profile=self.profile, 
            address_line_1='123 Payment St', 
            city='Paytown', 
            state='PY',
            postal_code='12345'
        )

        # Create a valid order
        self.order = Order.objects.create(
            user=self.user, 
            shipping_address=self.address, 
            total_price=150.75,
            status='Pending'
        )

        # URL for creating a payment intent
        self.create_intent_url = reverse('create-payment-intent')

    def test_create_payment_intent_success(self, mock_stripe_create):
        """
        Ensure a payment intent can be created successfully for a valid order.
        """
        # Configure the mock to return a successful response
        mock_stripe_create.return_value = {
            'id': 'pi_12345',
            'client_secret': 'cs_12345_secret',
            'amount': 15075,
            'currency': 'usd'
        }

        payload = {'order_id': self.order.id}
        response = self.client.post(self.create_intent_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('clientSecret', response.data)

        # Verify that stripe.PaymentIntent.create was called correctly
        mock_stripe_create.assert_called_once_with(
            amount=15075, # Amount in cents
            currency='usd',
            metadata={'order_id': self.order.id}
        )

    def test_create_payment_intent_invalid_order_id(self, mock_stripe_create):
        """
        Ensure the endpoint rejects an invalid or non-existent order ID.
        """
        invalid_order_id = 9999
        payload = {'order_id': invalid_order_id}
        response = self.client.post(self.create_intent_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(mock_stripe_create.called)

    def test_create_payment_intent_unauthenticated(self, mock_stripe_create):
        """
        Ensure unauthenticated users cannot create a payment intent.
        """
        self.client.logout()
        payload = {'order_id': self.order.id}
        response = self.client.post(self.create_intent_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(mock_stripe_create.called)

    def test_create_payment_intent_for_another_users_order(self, mock_stripe_create):
        """
        Ensure a user cannot create a payment intent for an order they do not own.
        """
        # Create another user and their order
        other_user = User.objects.create_user(username='otheruser', password='password123')
        other_order = Order.objects.create(
            user=other_user, 
            shipping_address=self.address, 
            total_price=50.00
        )

        # As self.user, try to create intent for other_order
        payload = {'order_id': other_order.id}
        response = self.client.post(self.create_intent_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(mock_stripe_create.called)

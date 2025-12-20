from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from mysite.orders.models import Order

User = get_user_model()

class PaymentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.order = Order.objects.create(user=self.user, total_price=100.00)
        self.url = reverse('create-payment-intent')

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_successfully(self, mock_stripe_create):
        """
        Ensure a payment intent is created successfully.
        """
        mock_stripe_create.return_value = {
            'client_secret': 'test_client_secret'
        }

        data = {'order_id': self.order.pk}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'clientSecret': 'test_client_secret'})

        mock_stripe_create.assert_called_once_with(
            amount=10000,  # in cents
            currency='usd',
            metadata={'order_id': self.order.pk}
        )

    def test_reject_invalid_order_id(self):
        """
        Ensure the endpoint rejects an invalid order ID.
        """
        data = {'order_id': 999} # Non-existent order
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_auth_required_for_payment_intent(self):
        """
        Ensure authentication is required to create a payment intent.
        """
        self.client.force_authenticate(user=None)
        data = {'order_id': self.order.pk}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

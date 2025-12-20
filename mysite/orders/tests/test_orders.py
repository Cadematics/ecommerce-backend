from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from mysite.products.models import Product, Category
from mysite.orders.models import Order, OrderItem
from mysite.cart.models import Cart, CartItem

User = get_user_model()

class OrderTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(name='Test Product', category=self.category, price=10.00, stock=10)

        # User 1's cart and items
        self.cart1 = Cart.objects.create(user=self.user1)
        self.cart_item1 = CartItem.objects.create(cart=self.cart1, product=self.product, quantity=2)

        self.client.force_authenticate(user=self.user1)

    def test_create_order_from_cart(self):
        """
        Ensure a user can create an order from their cart.
        """
        url = reverse('order-list')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

    def test_order_total_is_correct(self):
        """
        Ensure the total price of the order is calculated correctly.
        """
        url = reverse('order-list')
        response = self.client.post(url, format='json')
        order = Order.objects.get(pk=response.data['id'])
        self.assertEqual(order.total_price, self.product.price * self.cart_item1.quantity)

    def test_cart_is_cleared_after_order(self):
        """
        Ensure the user's cart is cleared after placing an order.
        """
        url = reverse('order-list')
        self.client.post(url, format='json')
        self.cart1.refresh_from_db()
        self.assertEqual(self.cart1.items.count(), 0)

    def test_user_can_only_see_their_orders(self):
        """
        Ensure a user can only list their own orders.
        """
        Order.objects.create(user=self.user2, total_price=50.00) # Another user's order
        url = reverse('order-list')
        self.client.post(url, format='json') # Create an order for user1
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_cannot_access_another_users_order(self):
        """
        Ensure a user cannot retrieve another user's order.
        """
        order2 = Order.objects.create(user=self.user2, total_price=50.00)
        url = reverse('order-detail', kwargs={'pk': order2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

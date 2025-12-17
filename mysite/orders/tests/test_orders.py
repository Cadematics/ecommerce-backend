from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ..models import Order, OrderItem
from cart.models import Cart, CartItem
from store.models import Product, Category
from users.models import Address, UserProfile

class OrderTests(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        
        # Create profiles and addresses
        self.profile1 = UserProfile.objects.create(user=self.user1)
        self.address1 = Address.objects.create(
            profile=self.profile1, 
            address_line_1='123 Main St', 
            city='Anytown', 
            state='CA',
            postal_code='12345',
            country='USA', 
            is_default=True
        )

        # Create products
        self.category = Category.objects.create(name='Books', slug='books')
        self.product1 = Product.objects.create(name='Django for Beginners', category=self.category, price=30.00, stock=10, is_active=True)
        self.product2 = Product.objects.create(name='DRF in Action', category=self.category, price=40.00, stock=5, is_active=True)

        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Populate user1's cart
        self.cart = Cart.objects.create(user=self.user1)
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2) # 2 * 30.00 = 60.00
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1) # 1 * 40.00 = 40.00
        # Expected total: 100.00

        # Create an order for user2 to test access permissions
        self.order2 = Order.objects.create(user=self.user2, shipping_address=self.address1, total_price=50.00)

        # URLs
        self.orders_url = reverse('order-list')
        self.order_detail_url_user2 = reverse('order-detail', kwargs={'pk': self.order2.id})

    def test_create_order_from_cart(self):
        """
        Ensure a user can create an order from their cart.
        """
        order_data = {'shipping_address_id': self.address1.id}
        response = self.client.post(self.orders_url, order_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.filter(user=self.user1).count(), 1)
        
        created_order = Order.objects.get(user=self.user1)
        self.assertEqual(created_order.order_items.count(), 2)
        self.assertEqual(created_order.total_price, 100.00)

    def test_cart_is_cleared_after_order_creation(self):
        """
        Ensure the user's cart is empty after an order is successfully created.
        """
        order_data = {'shipping_address_id': self.address1.id}
        self.client.post(self.orders_url, order_data, format='json')
        
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.items.count(), 0)

    def test_user_can_list_only_their_orders(self):
        """
        Ensure a user can list their own orders but not others'.
        """
        # Create an order for user1 first
        Order.objects.create(user=self.user1, shipping_address=self.address1, total_price=100.00)
        
        response = self.client.get(self.orders_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Should only see their own order
        self.assertEqual(response.data[0]['user'], self.user1.id)

    def test_user_cannot_access_another_users_order(self):
        """
        Ensure a user gets a 404 when trying to access another user's order detail.
        """
        response = self.client.get(self.order_detail_url_user2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_with_empty_cart(self):
        """
        Ensure creating an order with an empty cart is rejected.
        """
        # Clear the cart first
        self.cart.items.all().delete()
        
        order_data = {'shipping_address_id': self.address1.id}
        response = self.client.post(self.orders_url, order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('empty', response.data['detail'])

    def test_create_order_without_address(self):
        """
        Ensure creating an order without a shipping address is rejected.
        """
        order_data = {} # Missing shipping_address_id
        response = self.client.post(self.orders_url, order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('shipping_address_id', response.data)

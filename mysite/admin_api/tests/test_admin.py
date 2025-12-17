from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from store.models import Product, Category
from orders.models import Order

class AdminAPITests(APITestCase):
    def setUp(self):
        # Create a regular user (non-admin)
        self.user = User.objects.create_user(username='regularuser', password='password123')

        # Create an admin user
        self.admin_user = User.objects.create_user(username='adminuser', password='password123', is_staff=True)

        # Create initial data
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(name='Test Product', category=self.category, price=10.00, stock=5)
        self.order = Order.objects.create(user=self.user, total_price=50.00, status='Pending')

        # URLS
        self.admin_products_url = reverse('admin-product-list')
        self.admin_product_detail_url = reverse('admin-product-detail', kwargs={'pk': self.product.pk})
        self.admin_categories_url = reverse('admin-category-list')
        self.admin_category_detail_url = reverse('admin-category-detail', kwargs={'pk': self.category.pk})
        self.admin_orders_url = reverse('admin-order-list')
        self.admin_order_detail_url = reverse('admin-order-detail', kwargs={'pk': self.order.pk})

    def test_non_admin_cannot_access_admin_api(self):
        """
        Ensure non-admin users are rejected from all admin endpoints.
        """
        self.client.force_authenticate(user=self.user)
        
        # Product endpoints
        response = self.client.get(self.admin_products_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.post(self.admin_products_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(self.admin_product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Category endpoints
        response = self.client.get(self.admin_categories_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Order endpoints
        response = self.client.get(self.admin_orders_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_product(self):
        """
        Ensure admin users can create a new product.
        """
        self.client.force_authenticate(user=self.admin_user)
        product_data = {
            'name': 'New Admin Product',
            'category': self.category.id,
            'price': '99.99',
            'stock': 100,
            'is_active': True
        }
        response = self.client.post(self.admin_products_url, product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(name='New Admin Product').exists())

    def test_admin_can_update_product(self):
        """
        Ensure admin users can update an existing product.
        """
        self.client.force_authenticate(user=self.admin_user)
        update_data = {'price': '15.99', 'stock': 3}
        response = self.client.patch(self.admin_product_detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 15.99)
        self.assertEqual(self.product.stock, 3)

    def test_admin_can_delete_product(self):
        """
        Ensure admin users can delete a product.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.admin_product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_admin_can_update_order_status(self):
        """
        Ensure admin users can update the status of an order.
        """
        self.client.force_authenticate(user=self.admin_user)
        update_data = {'status': 'Shipped'}
        response = self.client.patch(self.admin_order_detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'Shipped')

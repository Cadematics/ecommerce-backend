from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from mysite.products.models import Product, Category
from mysite.orders.models import Order

User = get_user_model()

class AdminAPITests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpassword')
        self.regular_user = User.objects.create_user(username='user', email='user@example.com', password='userpassword')

        self.category = Category.objects.create(name='Admin Category')
        self.product = Product.objects.create(name='Admin Product', category=self.category, price=50.00)
        self.order = Order.objects.create(user=self.regular_user, total_price=100.00, status='Pending')

        self.product_list_url = reverse('admin-product-list')
        self.category_list_url = reverse('admin-category-list')
        self.order_detail_url = reverse('admin-order-detail', kwargs={'pk': self.order.pk})

    def test_admin_can_create_product(self):
        """
        Ensure an admin user can create a new product.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Admin Product', 'category': self.category.pk, 'price': 120.00}
        response = self.client.post(self.product_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_non_admin_is_rejected_from_creating_product(self):
        """
        Ensure a non-admin user is rejected from creating a product.
        """
        self.client.force_authenticate(user=self.regular_user)
        data = {'name': 'New Product Attempt', 'category': self.category.pk, 'price': 10.00}
        response = self.client.post(self.product_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_order_status(self):
        """
        Ensure an admin user can update the status of an order.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = {'status': 'Shipped'}
        response = self.client.patch(self.order_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'Shipped')

    def test_non_admin_is_rejected_from_updating_order(self):
        """
        Ensure a non-admin user is rejected from updating an order.
        """
        self.client.force_authenticate(user=self.regular_user)
        data = {'status': 'Shipped'}
        response = self.client.patch(self.order_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

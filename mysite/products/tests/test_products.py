from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from mysite.products.models import Category, Product

class ProductTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product1 = Product.objects.create(
            name='Test Product 1',
            category=self.category,
            price=10.00,
            is_active=True
        )
        self.product2 = Product.objects.create(
            name='Test Product 2',
            category=self.category,
            price=20.00,
            is_active=False  # Inactive product
        )
        self.product3 = Product.objects.create(
            name='Featured Product',
            category=self.category,
            price=30.00,
            is_active=True,
            is_featured=True
        )

    def test_public_can_list_categories(self):
        """
        Ensure public users can list all categories.
        """
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_public_can_list_active_products(self):
        """
        Ensure public users can list all active products.
        """
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only active products

    def test_public_can_retrieve_product(self):
        """
        Ensure public users can retrieve a single product.
        """
        url = reverse('product-detail', kwargs={'pk': self.product1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product1.name)

    def test_featured_endpoint_returns_featured_products(self):
        """
        Ensure the featured endpoint returns only featured products.
        """
        url = reverse('product-featured')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Featured Product')
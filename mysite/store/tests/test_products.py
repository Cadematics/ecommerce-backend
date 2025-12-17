from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Category, Product, Color

class ProductsPublicTests(APITestCase):
    def setUp(self):
        # Create data for testing
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.color_blue = Color.objects.create(name='Blue', hex_code='#0000FF')
        self.color_red = Color.objects.create(name='Red', hex_code='#FF0000')

        self.active_product = Product.objects.create(
            name='Active Laptop', 
            slug='active-laptop', 
            category=self.category, 
            price=1200.00, 
            is_active=True, 
            is_featured=False
        )
        self.active_product.colors.add(self.color_blue)

        self.featured_product = Product.objects.create(
            name='Featured Smartphone', 
            slug='featured-smartphone', 
            category=self.category, 
            price=800.00, 
            is_active=True, 
            is_featured=True
        )
        self.featured_product.colors.add(self.color_red)

        self.inactive_product = Product.objects.create(
            name='Inactive Tablet', 
            slug='inactive-tablet', 
            category=self.category, 
            price=500.00, 
            is_active=False
        )

        # URLs
        self.categories_url = reverse('category-list')
        self.products_url = reverse('product-list')
        self.featured_products_url = reverse('product-featured')
        self.product_detail_url = reverse('product-detail', kwargs={'slug': self.active_product.slug})
        self.inactive_product_detail_url = reverse('product-detail', kwargs={'slug': self.inactive_product.slug})


    def test_public_can_list_categories(self):
        """
        Ensure anyone can list product categories.
        """
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Electronics')

    def test_public_can_list_products_and_excludes_inactive(self):
        """
        Ensure anyone can list products, and inactive products are excluded.
        """
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return the active and featured products
        self.assertEqual(len(response.data['results']), 2) 
        product_names = [p['name'] for p in response.data['results']]
        self.assertIn('Active Laptop', product_names)
        self.assertNotIn('Inactive Tablet', product_names)

    def test_public_can_retrieve_active_product_detail(self):
        """
        Ensure anyone can view the detail of an active product.
        """
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.active_product.name)

    def test_public_cannot_retrieve_inactive_product_detail(self):
        """
        Ensure retrieving an inactive product results in a 404 error.
        """
        response = self.client.get(self.inactive_product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_featured_products(self):
        """
        Ensure the featured endpoint returns only featured products.
        """
        response = self.client.get(self.featured_products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.featured_product.name)
        self.assertTrue(response.data[0]['is_featured'])

    def test_filter_products_by_price(self):
        """
        Ensure products can be filtered by min_price and max_price.
        """
        # Filter for price >= 1000
        response = self.client.get(self.products_url, {'min_price': 1000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Active Laptop')

        # Filter for price <= 1000
        response = self.client.get(self.products_url, {'max_price': 1000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Featured Smartphone')

    def test_filter_products_by_color(self):
        """
        Ensure products can be filtered by color slug.
        """
        response = self.client.get(self.products_url, {'color': 'blue'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Active Laptop')

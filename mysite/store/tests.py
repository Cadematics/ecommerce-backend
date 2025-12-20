from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Category, Product

class PublicApiTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.active_product = Product.objects.create(
            name='Active Product', 
            category=self.category, 
            price=100.00, 
            is_active=True
        )
        self.inactive_product = Product.objects.create(
            name='Inactive Product', 
            category=self.category, 
            price=200.00, 
            is_active=False
        )
        self.featured_product = Product.objects.create(
            name='Featured Product', 
            category=self.category, 
            price=300.00, 
            is_active=True, 
            is_featured=True
        )
        self.colored_product = Product.objects.create(
            name='Colored Product', 
            category=self.category, 
            price=400.00, 
            is_active=True,
            color='Blue'
        )

        self.categories_url = reverse('category-list')
        self.products_url = reverse('product-list')
        self.featured_products_url = reverse('featured-product-list')

    def test_public_can_list_categories(self):
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_public_can_list_products(self):
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inactive_products_are_excluded(self):
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product_names = [p['name'] for p in response.data['results']]
        self.assertNotIn('Inactive Product', product_names)

    def test_get_featured_products(self):
        response = self.client.get(self.featured_products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Featured Product')

    def test_filter_products_by_price(self):
        response = self.client.get(self.products_url, {'price_min': 150})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_products_by_color(self):
        response = self.client.get(self.products_url, {'color': 'Blue'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Colored Product')

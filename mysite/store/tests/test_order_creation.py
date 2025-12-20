
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from mysite.store.models import Category, Product

class OrderCreationTest(APITestCase):

    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=50.00,
            is_active=True,
            stock_quantity=10
        )

    def test_create_product(self):
        """
        Ensure we can create a product.
        """
        print("Product ID:", self.product.id)
        self.assertIsNotNone(self.product.id)


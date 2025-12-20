
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Cart, CartItem
from store.models import Product, Category

User = get_user_model()

class CartApiTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Test Category')
        self.active_product = Product.objects.create(
            name='Active Product', 
            category=self.category, 
            price=10.00, 
            stock_quantity=10, 
            is_active=True
        )
        self.inactive_product = Product.objects.create(
            name='Inactive Product', 
            category=self.category, 
            price=20.00, 
            stock_quantity=5, 
            is_active=False
        )
        self.out_of_stock_product = Product.objects.create(
            name='Out of Stock Product', 
            category=self.category, 
            price=30.00, 
            stock_quantity=0, 
            is_active=True
        )

        self.cart_url = reverse('cart-detail')
        self.cart_items_url = reverse('cart-items')
        self.cart_clear_url = reverse('cart-clear')

    def test_cart_auto_creates_for_new_user(self):
        self.assertTrue(Cart.objects.filter(user=self.user).exists())

    def test_authenticated_user_can_view_cart(self):
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)

    def test_add_item_to_cart(self):
        item_data = {
            'product_id': self.active_product.id,
            'quantity': 2
        }
        response = self.client.post(self.cart_items_url, item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cart.objects.get(user=self.user).items.count(), 1)
        self.assertEqual(CartItem.objects.first().quantity, 2)

    def test_cannot_add_inactive_item_to_cart(self):
        item_data = {
            'product_id': self.inactive_product.id,
            'quantity': 1
        }
        response = self.client.post(self.cart_items_url, item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_add_out_of_stock_item_to_cart(self):
        item_data = {
            'product_id': self.out_of_stock_product.id,
            'quantity': 1
        }
        response = self.client.post(self.cart_items_url, item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock', response.data['non_field_errors'][0].lower())

    def test_update_cart_item_quantity(self):
        cart_item = CartItem.objects.create(
            cart=Cart.objects.get(user=self.user),
            product=self.active_product, 
            quantity=1
        )
        item_detail_url = reverse('cart-item-detail', kwargs={'pk': cart_item.id})
        update_data = {'quantity': 5}

        response = self.client.put(item_detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_remove_item_from_cart(self):
        cart_item = CartItem.objects.create(
            cart=Cart.objects.get(user=self.user),
            product=self.active_product, 
            quantity=1
        )
        item_detail_url = reverse('cart-item-detail', kwargs={'pk': cart_item.id})

        response = self.client.delete(item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(pk=cart_item.id).exists())

    def test_clear_cart(self):
        CartItem.objects.create(cart=Cart.objects.get(user=self.user), product=self.active_product, quantity=2)
        
        response = self.client.delete(self.cart_clear_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cart.objects.get(user=self.user).items.count(), 0)

    def test_unauthenticated_access_to_cart_is_rejected(self):
        self.client.logout()
        response_get = self.client.get(self.cart_url)
        response_post = self.client.post(self.cart_items_url, {}, format='json')
        
        self.assertEqual(response_get.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_post.status_code, status.HTTP_401_UNAUTHORIZED)

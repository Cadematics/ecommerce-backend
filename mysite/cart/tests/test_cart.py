from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ..models import Cart, CartItem
from store.models import Product, Category, Size, Color

class CartTests(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testcartuser', password='password123')
        self.client.force_authenticate(user=self.user)

        # Create product data
        self.category = Category.objects.create(name='Apparel', slug='apparel')
        self.size = Size.objects.create(name='Medium', code='M')
        self.color = Color.objects.create(name='Black', hex_code='#000000')

        self.active_product = Product.objects.create(
            name='T-Shirt', 
            slug='t-shirt',
            category=self.category, 
            price=25.00, 
            stock=10, 
            is_active=True
        )
        self.active_product.sizes.add(self.size)
        self.active_product.colors.add(self.color)
        
        self.out_of_stock_product = Product.objects.create(
            name='Sold Out Hat', 
            slug='sold-out-hat', 
            category=self.category, 
            price=30.00, 
            stock=0, 
            is_active=True
        )

        # URLs
        self.cart_url = reverse('cart-detail')
        self.cart_items_url = reverse('cart-item-list')
        self.cart_clear_url = reverse('cart-clear')

    def test_cart_is_auto_created_for_user(self):
        """
        Ensure a cart is automatically created for a user upon first access.
        """
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Cart.objects.filter(user=self.user).exists())

    def test_add_item_to_cart(self):
        """
        Ensure a user can add a valid product to their cart.
        """
        item_data = {
            'product_id': self.active_product.id,
            'size_id': self.size.id,
            'color_id': self.color.id,
            'quantity': 1
        }
        response = self.client.post(self.cart_items_url, item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().product, self.active_product)

    def test_cannot_add_out_of_stock_item_to_cart(self):
        """
        Ensure adding an out-of-stock product to the cart is rejected.
        """
        item_data = {
            'product_id': self.out_of_stock_product.id,
            'quantity': 1
        }
        response = self.client.post(self.cart_items_url, item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock', response.data['non_field_errors'][0])

    def test_update_cart_item_quantity(self):
        """
        Ensure the quantity of an item in the cart can be updated.
        """
        # First, add an item
        cart_item = CartItem.objects.create(
            cart=Cart.objects.get_or_create(user=self.user)[0],
            product=self.active_product, 
            quantity=1
        )
        item_detail_url = reverse('cart-item-detail', kwargs={'pk': cart_item.id})
        
        update_data = {'quantity': 3}
        response = self.client.put(item_detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 3)

    def test_remove_item_from_cart(self):
        """
        Ensure an item can be removed from the cart.
        """
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
        """
        Ensure the entire cart can be cleared of all items.
        """
        CartItem.objects.create(cart=Cart.objects.get(user=self.user), product=self.active_product, quantity=2)
        
        response = self.client.delete(self.cart_clear_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cart.objects.get(user=self.user).items.count(), 0)

    def test_unauthenticated_access_to_cart_is_rejected(self):
        """
        Ensure unauthenticated users cannot access cart endpoints.
        """
        self.client.logout()
        response_get = self.client.get(self.cart_url)
        response_post = self.client.post(self.cart_items_url, {}, format='json')
        
        self.assertEqual(response_get.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response_post.status_code, status.HTTP_401_UNAUTHORIZED)

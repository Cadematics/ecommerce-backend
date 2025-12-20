from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from mysite.products.models import Product, Category
from mysite.cart.models import Cart, CartItem

User = get_user_model()

class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(name='Test Product', category=self.category, price=10.00, stock=10, is_active=True)
        self.inactive_product = Product.objects.create(name='Inactive Product', category=self.category, price=10.00, is_active=False)

        self.cart_url = reverse('cart-detail')
        self.cart_items_url = reverse('cartitem-list')

    def test_cart_autocreates_for_user(self):
        """
        Ensure a cart is automatically created for a user.
        """
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Cart.objects.filter(user=self.user).exists())

    def test_add_item_to_cart(self):
        """
        Ensure a user can add an item to their cart.
        """
        data = {'product': self.product.pk, 'quantity': 2}
        response = self.client.post(self.cart_items_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user.cart.items.count(), 1)

    def test_update_cart_item_quantity(self):
        """
        Ensure a user can update the quantity of a cart item.
        """
        cart_item = CartItem.objects.create(cart=self.user.cart, product=self.product, quantity=1)
        url = reverse('cartitem-detail', kwargs={'pk': cart_item.pk})
        data = {'quantity': 5}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_remove_item_from_cart(self):
        """
        Ensure a user can remove an item from their cart.
        """
        cart_item = CartItem.objects.create(cart=self.user.cart, product=self.product, quantity=1)
        url = reverse('cartitem-detail', kwargs={'pk': cart_item.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.cart.items.count(), 0)

    def test_clear_cart(self):
        """
        Ensure a user can clear their entire cart.
        """
        CartItem.objects.create(cart=self.user.cart, product=self.product, quantity=1)
        url = reverse('cart-clear')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.cart.items.count(), 0)

    def test_cannot_add_inactive_product_to_cart(self):
        """
        Ensure an inactive product cannot be added to the cart.
        """
        data = {'product': self.inactive_product.pk, 'quantity': 1}
        response = self.client.post(self.cart_items_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_access_rejected(self):
        """
        Ensure unauthenticated users cannot access the cart.
        """
        self.client.force_authenticate(user=None)
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

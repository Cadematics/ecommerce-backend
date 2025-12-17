from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from users.models import Address
from cart.models import Cart, CartItem
from users.serializers import AddressSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model. Used for displaying order items.
    """
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'price', 'quantity']

class OrderReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading and displaying Orders.
    Includes nested representations for items and shipping address.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_amount', 'shipping_address', 'items', 'created_at', 'updated_at']

class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new Order from the user's cart.
    Handles the entire order creation logic, including cart validation,
    total calculation, data snapshotting, and cart clearing.
    """
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        write_only=True,
        label="Shipping Address"
    )

    def validate_address_id(self, address):
        """
        Validate that the shipping address belongs to the requesting user.
        """
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("Request context is missing for validation.")
        
        if address.user != request.user:
            raise serializers.ValidationError("The provided shipping address does not belong to the current user.")
        return address

    def create(self, validated_data):
        """
        Create an order using an atomic transaction.
        - Fetches the user's cart.
        - Calculates the total amount.
        - Creates the Order and OrderItem instances.
        - Clears the user's cart.
        """
        request = self.context.get('request')
        user = request.user
        shipping_address = validated_data['address_id']

        try:
            cart = Cart.objects.get(user=user)
            cart_items = cart.items.all()
        except Cart.DoesNotExist:
            raise serializers.ValidationError("User does not have a cart.")

        if not cart_items.exists():
            raise serializers.ValidationError("Cannot create an order with an empty cart.")

        # Calculate total amount from cart items
        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        with transaction.atomic():
            # Create the Order
            order = Order.objects.create(
                user=user,
                shipping_address=shipping_address,
                total_amount=total_amount,
                status='pending'  # Default status
            )

            # Create OrderItems by snapshotting product data
            order_items_to_create = [
                OrderItem(
                    order=order,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity,
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items_to_create)

            # Clear the cart
            cart.items.all().delete()
            cart.delete()

        return order


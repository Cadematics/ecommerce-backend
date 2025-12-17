from rest_framework import serializers
from .models import Cart, CartItem
from store.serializers import ProductSerializer
from store.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            if not product.is_active or product.stock == 0:
                raise serializers.ValidationError("Product is not available.")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        return value

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']

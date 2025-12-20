from rest_framework import serializers
from .models import Cart, CartItem
from store.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ('id', 'product_id', 'quantity', 'item_total')
        read_only_fields = ('id', 'item_total')

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        return value

    def validate(self, data):
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        product = Product.objects.get(id=product_id)

        if not product.is_active:
            raise serializers.ValidationError("This product is not active.")
        if product.stock_quantity < quantity:
            raise serializers.ValidationError("Not enough stock available.")

        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_cost')
        read_only_fields = ('id', 'user', 'total_cost')

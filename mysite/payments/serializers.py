from rest_framework import serializers
from orders.models import Order

class PaymentIntentCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a Stripe PaymentIntent.
    Validates that the order exists and belongs to the authenticated user.
    """
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        label="Order ID"
    )

    def validate_order_id(self, order):
        """
        Validate that the order belongs to the requesting user and is in a 'pending' state.
        """
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("Request context is missing for validation.")

        if order.user != request.user:
            raise serializers.ValidationError("This order does not belong to the authenticated user.")

        if order.status != 'pending':
            raise serializers.ValidationError("Payment can only be initiated for orders with a 'pending' status.")

        return order

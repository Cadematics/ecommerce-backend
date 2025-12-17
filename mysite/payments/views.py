import stripe
from django.conf import settings
from rest_framework import views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import PaymentIntentCreateSerializer

# Set the Stripe API key from Django settings
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripePaymentIntentCreateView(views.APIView):
    """
    API view to create a Stripe PaymentIntent.

    - Validates the order.
    - Creates a PaymentIntent with the correct amount and currency.
    - Attaches the order_id to the PaymentIntent metadata.
    - Returns the client_secret to the frontend.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentIntentCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.validated_data['order_id']

        # Convert order total to cents (or the smallest currency unit)
        try:
            amount_in_cents = int(order.total_amount * 100)
        except Exception as e:
            return Response(
                {"error": "Invalid order total amount."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency=settings.STRIPE_CURRENCY,
                automatic_payment_methods={"enabled": True},
                metadata={
                    'order_id': order.id,
                    'user_id': request.user.id
                }
            )

            # Update order status to 'pending_payment' or a similar status if needed
            # For MVP, we keep it simple until payment is confirmed.

            return Response(
                {'client_secret': intent.client_secret},
                status=status.HTTP_201_CREATED
            )

        except stripe.error.StripeError as e:
            return Response(
                {"error": f"Stripe error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StripeConfirmView(views.APIView):
    """
    Placeholder for handling payment confirmations, intended to be used with webhooks.
    For MVP, this endpoint is not fully implemented.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # In a real-world scenario, this logic would be in a webhook handler
        # that is not exposed to the public internet without verification.
        # For now, this is a placeholder.
        return Response({"message": "Webhook confirmation pending implementation."}, status=status.HTTP_501_NOT_IMPLEMENTED)

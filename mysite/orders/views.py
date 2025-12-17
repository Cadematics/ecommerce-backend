from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order
from .serializers import OrderReadSerializer, OrderCreateSerializer

class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    """
    A ViewSet for creating, listing, and retrieving orders.

    - POST /api/orders/: Creates a new order from the user's cart.
    - GET /api/orders/: Lists all orders for the authenticated user.
    - GET /api/orders/{id}/: Retrieves a specific order.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the request action.
        - Use OrderCreateSerializer for the 'create' action.
        - Use OrderReadSerializer for all other actions.
        """
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderReadSerializer

    def get_queryset(self):
        """
        This view should return a list of all the orders for the currently authenticated user.
        We also prefetch related items to optimize performance and prevent N+1 queries.
        """
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items', 'shipping_address'
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """
        Create an order using the OrderCreateSerializer.
        The serializer handles all the business logic, including validating the cart,
        calculating the total, snapshotting data, and clearing the cart.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        # After creation, we want to return the detailed order view
        read_serializer = OrderReadSerializer(order, context={'request': request})
        headers = self.get_success_headers(read_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

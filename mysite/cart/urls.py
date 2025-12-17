from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartView, CartItemViewSet, ClearCartView

router = DefaultRouter()
router.register(r'items', CartItemViewSet, basename='cart-item')

urlpatterns = [
    path('', CartView.as_view(), name='cart-detail'),
    path('clear/', ClearCartView.as_view(), name='cart-clear'),
    path('', include(router.urls)),
]

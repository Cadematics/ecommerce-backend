from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartDetailView.as_view(), name='cart-detail'),
    path('items/', views.CartItemView.as_view(), name='cart-items'),
    path('items/<int:pk>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
    path('clear/', views.CartClearView.as_view(), name='cart-clear'),
]

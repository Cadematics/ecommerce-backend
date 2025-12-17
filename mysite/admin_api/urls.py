from django.urls import path
from .views import (
    AdminProductListCreateView,
    AdminProductRetrieveUpdateDestroyView,
    AdminCategoryListCreateView,
    AdminCategoryRetrieveUpdateDestroyView,
    AdminOrderListView,
    AdminOrderUpdateStatusView,
)

app_name = 'admin_api'

urlpatterns = [
    path('products/', AdminProductListCreateView.as_view(), name='admin-product-list-create'),
    path('products/<int:pk>/', AdminProductRetrieveUpdateDestroyView.as_view(), name='admin-product-detail'),
    path('categories/', AdminCategoryListCreateView.as_view(), name='admin-category-list-create'),
    path('categories/<int:pk>/', AdminCategoryRetrieveUpdateDestroyView.as_view(), name='admin-category-detail'),
    path('orders/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('orders/<int:pk>/status/', AdminOrderUpdateStatusView.as_view(), name='admin-order-status-update'),
]

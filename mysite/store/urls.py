from django.urls import path
from .views import (
    CategoryListView,
    ProductListView,
    ProductDetailView,
    FeaturedProductListView,
    LandingPageView
)

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing-page'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/featured/', FeaturedProductListView.as_view(), name='featured-product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]

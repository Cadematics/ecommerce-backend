from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .filters import ProductFilter
from django.shortcuts import render
from django.views.generic import ListView, View
from .pagination import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend

class LandingPageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'landing.html')

class ProductList(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = StandardResultsSetPagination

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

class FeaturedProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True, is_featured=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

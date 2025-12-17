from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_max = filters.NumberFilter(field_name="price", lookup_expr='lte')
    color = filters.CharFilter(field_name='color', lookup_expr='iexact')

    class Meta:
        model = Product
        fields = ['color', 'price_min', 'price_max']

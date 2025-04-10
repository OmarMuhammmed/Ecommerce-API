import django_filters.rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    class Meta:
        model = Product
        fields = ['category', 'name', 'price', 'quantity']
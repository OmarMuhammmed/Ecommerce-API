from rest_framework import permissions, viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.throttling import ScopedRateThrottle

from .filters import ProductFilter
from products.models import Product, ProductCategory
from products.permissions import IsSellerOrAdmin
from products.serializers import (
    ProductCategoryReadSerializer,
    ProductReadSerializer,
    ProductWriteSerializer,
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from rest_framework import permissions, viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

@extend_schema(tags=["Products"])
class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = ProductCategory.objects.all()  
    serializer_class = ProductCategoryReadSerializer  
    @method_decorator(cache_page(60 * 15))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))  
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

@extend_schema(tags=["Products"])
class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD products
    """

    queryset = Product.objects.select_related('category').all()
    search_fields = ['name', 'description', 'category__name']
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = ProductFilter
    
    def get_throttles(self):
        if self.action == "list":
            throttle = ScopedRateThrottle()
            throttle.scope = 'search_filiter'  
            return [throttle]
        return super().get_throttles()
    
    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return ProductWriteSerializer

        return ProductReadSerializer

    def get_permissions(self):
        if self.action in ("create",):
            self.permission_classes = (permissions.IsAuthenticated,)
        elif self.action in ("update", "partial_update", "destroy"):
            self.permission_classes = (IsSellerOrAdmin,)
        else:
            self.permission_classes = (permissions.AllowAny,)

        return super().get_permissions()

    @method_decorator(cache_page(60 * 5))  
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 5)) 
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)



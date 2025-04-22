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
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

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

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

@extend_schema(tags=["Products"])
class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD products
    """

    queryset = Product.objects.select_related('category').all()
    search_fields = ['name', 'desc', 'category__name']
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='q',
                description='Search query for full-text search in product name and description',
                required=True,
                type=OpenApiTypes.STR
            )
        ],
        description='Full-text search for products using PostgreSQL search capabilities',
        responses={200: ProductReadSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Full-text search endpoint for products
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Please provide a search query'}, status=400)
            
        search_query = SearchQuery(query)
        
        # Search in both name and desc fields with different weights
        products = Product.objects.annotate(
            rank=SearchRank('search_vector', search_query)
        ).filter(search_vector=search_query).order_by('-rank')
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)



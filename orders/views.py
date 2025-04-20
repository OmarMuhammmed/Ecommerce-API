from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
import hashlib


from orders.models import Order, OrderItem
from orders.permissions import (
    IsOrderByBuyerOrAdmin,
    IsOrderItemByBuyerOrAdmin,
    IsOrderItemPending,
    IsOrderPending,
)
from orders.serializers import (
    OrderItemSerializer,
    OrderReadSerializer,
    OrderWriteSerializer,
)
from .throttling import OrderItemRateThrottle, OrderRateThrottle




@extend_schema(tags=["Orders"])
class OrderItemViewSet(viewsets.ModelViewSet):
    """
    CRUD order items that are associated with the current order id.
    """
    queryset = OrderItem.objects.select_related('order')
    serializer_class = OrderItemSerializer
    permission_classes = [IsOrderItemByBuyerOrAdmin]
    throttle_classes = [OrderItemRateThrottle]
    
    def get_queryset(self):
        order_id = self.kwargs.get("order_id")
        return super().get_queryset().filter(order__id=order_id)
    
    def perform_create(self, serializer):
        order = get_object_or_404(Order, id=self.kwargs.get("order_id"))
        serializer.save(order=order)
    
    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permission() for permission in self.permission_classes] + [IsOrderItemPending()]
        return [permission() for permission in self.permission_classes]


@extend_schema(tags=["Orders"])
class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD orders of a user
    """
    queryset = Order.objects.select_related('buyer')
    permission_classes = [IsOrderByBuyerOrAdmin]
    throttle_classes = [OrderRateThrottle]
    
    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return OrderWriteSerializer
        return OrderReadSerializer
    
    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(buyer=user)
    
    def create(self, request, *args, **kwargs):
        
        idempotency_key = request.headers.get('Idempotency-Key')
        
        if not idempotency_key:
            return Response(
                {"error": "Idempotency-Key header is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a unique key combining the user ID and the idempotency key
        user_id = request.user.id
        unique_key = f"{user_id}:{idempotency_key}"
        hashed_key = hashlib.md5(unique_key.encode()).hexdigest()
        
        # Check if an order with this idempotency key already exists
        existing_order = Order.objects.filter(
            buyer=request.user,
            idempotency_key=hashed_key
        ).first()
        
        if existing_order:
            # Return the existing order
            serializer = self.get_serializer(existing_order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create a new order
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, hashed_key)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer, idempotency_key=None):
        serializer.save(buyer=self.request.user, idempotency_key=idempotency_key)
    
    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [permission() for permission in self.permission_classes] + [IsOrderPending()]
        return [permission() for permission in self.permission_classes]
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema


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
    
    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [permission() for permission in self.permission_classes] + [IsOrderPending()]
        return [permission() for permission in self.permission_classes]
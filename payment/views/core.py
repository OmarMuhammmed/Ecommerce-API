from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.viewsets import ModelViewSet

from orders.models import Order
from orders.permissions import IsOrderByBuyerOrAdmin
from payment.models import Payment
from payment.permissions import (
    IsOrderPendingWhenCheckout,
    IsPaymentByUser,
    IsPaymentPending,
)
from payment.serializers import CheckoutSerializer, PaymentSerializer
from payment.tasks import send_payment_success_email_task
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Payment"])
class PaymentViewSet(ModelViewSet):
    """
    CRUD payment for an order
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsPaymentByUser]

    def get_queryset(self):
        res = super().get_queryset()
        user = self.request.user
        return res.filter(order__buyer=user)

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            self.permission_classes += [IsPaymentPending]
        return super().get_permissions()

@extend_schema(tags=["Payment"])
class CheckoutAPIView(RetrieveUpdateAPIView):
    """
    Create, Retrieve, Update billing address, shipping address and payment of an order
    """
    queryset = Order.objects.all()
    serializer_class = CheckoutSerializer
    permission_classes = [IsOrderByBuyerOrAdmin]

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            self.permission_classes += [IsOrderPendingWhenCheckout]
        return super().get_permissions()


class OrderProcessor:
    """Handles order processing after successful payment"""
    
    @staticmethod
    def complete_order(order_id, customer_email, external_payment_id=None):
        """
        Complete the order process after successful payment
        """
        payment = get_object_or_404(Payment, order=order_id)
        payment.status = Payment.COMPLETED
        
        if external_payment_id:
            payment.external_payment_id = external_payment_id
            
        payment.save()
        
        order = get_object_or_404(Order, id=order_id)
        order.status = "C"  # Completed status for Order
        order.save()
        
        OrderProcessor._update_product_inventory(order)
        
        send_payment_success_email_task.delay(customer_email)
        
        return order
    
    @staticmethod
    def _update_product_inventory(order):
        """
        Update inventory for products in the order
        """
        for order_item in order.order_items.all():
            product = order_item.product
            if product.quantity >= order_item.quantity:
                product.quantity -= order_item.quantity
                product.save()
            else:
                print(f"Error: Not enough stock for {product.name}")
    
    @staticmethod
    def mark_payment_failed(order_id):
        """
        Mark a payment as failed
        """
        try:
            payment = Payment.objects.get(order_id=order_id)
            payment.status = Payment.FAILED
            payment.save()
        except Payment.DoesNotExist:
            pass
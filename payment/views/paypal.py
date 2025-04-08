import paypalrestsdk
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .base import PaymentGateway
from .core import OrderProcessor
from .factories import PaymentGatewayFactory
from orders.models import Order
from payment.models import Payment
from payment.permissions import (
    IsPaymentForOrderNotCompleted,
    DoesOrderHaveAddress,
)
from drf_spectacular.utils import extend_schema

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET
})

class PayPalGateway(PaymentGateway):
    """PayPal payment gateway implementation"""
    
    def get_payment_option_code(self):
        return Payment.PAYPAL
    
    def create_checkout_session(self, order):
        items = self._prepare_line_items(order)
        total_amount = sum(float(item["price"]) * float(item["quantity"]) for item in items)
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": f"{settings.BACKEND_DOMAIN}/api/payment/paypal/success/?order_id={order.id}",
                "cancel_url": f"{settings.BACKEND_DOMAIN}/api/payment/paypal/cancel/?order_id={order.id}"
            },
            "transactions": [{
                "item_list": {"items": items},
                "amount": {"total": str(total_amount), "currency": "USD"},
                "description": f"Payment for Order #{order.id}"
            }]
        })
        
        if payment.create():
            approval_url = next((link.href for link in payment.links if link.rel == "approval_url"), None)
            try:
                order_payment = Payment.objects.get(order_id=order.id)
                order_payment.external_payment_id = payment.id
                order_payment.save()
            except Payment.DoesNotExist:
                Payment.objects.create(
                    order=order,
                    status=Payment.PENDING,
                    payment_option=self.get_payment_option_code(),
                    external_payment_id=payment.id
                )
            return {"approval_url": approval_url, "payment_id": payment.id}
        else:
            return {"error": payment.error}
    
    def _prepare_line_items(self, order):
        items = []
        for order_item in order.order_items.all():
            product = order_item.product
            quantity = order_item.quantity
            item = {
                "name": product.name,
                "description": product.desc[:127],
                "quantity": str(quantity),
                "price": str(product.price / 100),
                "currency": "USD"
            }
            items.append(item)
        return items
    
    def process_successful_payment(self, order_id, payment_data=None):
        payment = Payment.objects.get(order_id=order_id)
        customer_email = payment.order.buyer.email
        external_payment_id = payment.external_payment_id
        return OrderProcessor.complete_order(order_id, customer_email, external_payment_id)
    
    def execute_payment(self, payment_id, payer_id):
        payment = paypalrestsdk.Payment.find(payment_id)
        return payment.execute({"payer_id": payer_id})


@extend_schema(tags=["Payment"])
class PayPalCheckoutSessionCreateAPIView(APIView):
    permission_classes = (IsPaymentForOrderNotCompleted, DoesOrderHaveAddress)

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs.get("order_id"))
        gateway = PaymentGatewayFactory.get_gateway('paypal')
        result = gateway.create_checkout_session(order)
        
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        request.session['paypal_payment_id'] = result["payment_id"]
        return Response(result, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Payment"])
class PayPalSuccessAPIView(APIView):
    def get(self, request, *args, **kwargs):
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')
        order_id = request.GET.get('order_id')
        
        if not payment_id or not payer_id or not order_id:
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)
        
        gateway = PaymentGatewayFactory.get_gateway('paypal')
        if gateway.execute_payment(payment_id, payer_id):
            gateway.process_successful_payment(order_id)
            return Response({"message": "Payment successful."}, status=status.HTTP_200_OK)
        else:
            OrderProcessor.mark_payment_failed(order_id)
            return Response({"error": "Payment execution failed"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Payment"])
class PayPalCancelAPIView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = request.GET.get('order_id')
        if order_id:
            OrderProcessor.mark_payment_failed(order_id)
        return Response({"message": "Oops! Payment cancelled."}, status=status.HTTP_200_OK)


@extend_schema(tags=["Payment"])
class PayPalWebhookAPIView(APIView):
    """
    PayPal webhook API view to handle payment events
    """
    def post(self, request, *args, **kwargs):
        try:
            event_data = request.data
            event_type = event_data.get('event_type')
            
            if event_type == 'PAYMENT.SALE.COMPLETED':
                resource = event_data.get('resource', {})
                payment_id = resource.get('parent_payment')
                
                try:
                    payment = Payment.objects.get(external_payment_id=payment_id)
                    order_id = payment.order.id
                    
                    gateway = PaymentGatewayFactory.get_gateway_for_payment(payment)
                    gateway.process_successful_payment(order_id)
                    
                except Payment.DoesNotExist:
                    print(f"Payment with PayPal ID {payment_id} not found")
            
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error processing PayPal webhook: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
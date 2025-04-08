import stripe
import json
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

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeGateway(PaymentGateway):
    def get_payment_option_code(self):
        return Payment.STRIPE
    
    def create_checkout_session(self, order):
        order_items = self._prepare_line_items(order)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=order_items,
            metadata={"order_id": order.id},
            mode="payment",
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
        )
        try:
            payment = Payment.objects.get(order_id=order.id)
            payment.external_payment_id = checkout_session["id"]
            payment.save()
        except Payment.DoesNotExist:
            Payment.objects.create(
                order=order,
                status=Payment.PENDING,
                payment_option=self.get_payment_option_code(),
                external_payment_id=checkout_session["id"]
            )
        return {"sessionId": checkout_session["id"]}
    
    def _prepare_line_items(self, order):
        order_items = []
        for order_item in order.order_items.all():
            product = order_item.product
            quantity = order_item.quantity
            data = {
                "price_data": {
                    "currency": "usd",
                    "unit_amount_decimal": product.price,
                    "product_data": {
                        "name": product.name,
                        "description": product.desc,
                        "images": [f"{settings.BACKEND_DOMAIN}{product.image.url}"],
                    },
                },
                "quantity": quantity,
            }
            order_items.append(data)
        return order_items
    
    def process_successful_payment(self, order_id, payment_data):
        session = payment_data["data"]["object"]
        customer_email = session["customer_details"]["email"]
        external_payment_id = session["id"]
        return OrderProcessor.complete_order(order_id, customer_email, external_payment_id)
    
    def verify_webhook_signature(self, payload, sig_header):
        try:
            return stripe.Webhook.construct_event(
                payload, 
                sig_header, 
                settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return None

@extend_schema(tags=["Payment"])
class StripeCheckoutSessionCreateAPIView(APIView):
    permission_classes = (IsPaymentForOrderNotCompleted, DoesOrderHaveAddress)

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs.get("order_id"))
        gateway = PaymentGatewayFactory.get_gateway('stripe')
        result = gateway.create_checkout_session(order)
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_201_CREATED)

@extend_schema(tags=["Payment"])
class StripeWebhookAPIView(APIView):
    def post(self, request, format=None):
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        gateway = PaymentGatewayFactory.get_gateway('stripe')
        event = gateway.verify_webhook_signature(payload, sig_header)
        
        if not event:
            try:
                event = json.loads(payload.decode('utf-8'))
            except json.JSONDecodeError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if event["type"] == "checkout.session.completed":
            order_id = event["data"]["object"]["metadata"]["order_id"]
            gateway.process_successful_payment(order_id, event)
        
        return Response(status=status.HTTP_200_OK)

@extend_schema(tags=["Payment"])
class StripeSuccessAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Payment successful."}, status=status.HTTP_200_OK)

@extend_schema(tags=["Payment"])
class StripeCancelAPIView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = request.GET.get('order_id')
        if order_id:
            OrderProcessor.mark_payment_failed(order_id)
        return Response({"message": "Oops! Payment cancelled."}, status=status.HTTP_200_OK)
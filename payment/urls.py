from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.core import (
    CheckoutAPIView,
    PaymentViewSet,
)
from .views.paypal import (
    PayPalCancelAPIView,
    PayPalCheckoutSessionCreateAPIView,
    PayPalSuccessAPIView,
    PayPalWebhookAPIView,
)
from .views.stripe import (
    StripeCancelAPIView,
    StripeCheckoutSessionCreateAPIView,
    StripeSuccessAPIView,
    StripeWebhookAPIView,   
)


router = DefaultRouter()
router.register(r"", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("checkout/<int:pk>/", CheckoutAPIView.as_view(), name="checkout"),
    
    # --- STRIPE --- 
    path(
        "stripe/create<int:order_id>/",
        StripeCheckoutSessionCreateAPIView.as_view(),
        name="checkout_session",
    ),
    path("stripe/webhook/", StripeWebhookAPIView.as_view(), name="stripe_webhook"),
    path('checkout/stripe/sucess/',StripeSuccessAPIView.as_view(), name='stripe_success'),
    path('checkout/stripe/cancel/',StripeCancelAPIView.as_view(), name='stripe_cancel'),
    
    # --- PAYPAL --- 
    path(
        "paypal/create/<int:order_id>/",
        PayPalCheckoutSessionCreateAPIView.as_view(),
        name="paypal_checkout_session",
    ),
    path("paypal/webhook/", PayPalWebhookAPIView.as_view(), name="paypal_webhook"),
    path('checkout/paypal/sucess/',PayPalSuccessAPIView.as_view(), name='paypal_success'),
    path('checkout/paypal/cancel/',PayPalCancelAPIView.as_view(), name='paypal_cancel'),
]

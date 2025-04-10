from rest_framework.throttling import ScopedRateThrottle


class PaymentSessionCreateThrottle(ScopedRateThrottle):
    scope = "payment_session_create"
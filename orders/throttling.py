from rest_framework.throttling import ScopedRateThrottle


class OrderItemRateThrottle(ScopedRateThrottle):
    scope = 'create_order'


class OrderRateThrottle(ScopedRateThrottle):
    scope = 'create_order'

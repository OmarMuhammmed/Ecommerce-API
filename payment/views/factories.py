from payment.models import Payment

class PaymentGatewayFactory:
    """Factory to create payment gateway instances"""
    
    @staticmethod
    def get_gateway(gateway_type):
        from .paypal import PayPalGateway
        from .stripe import StripeGateway

        gateways = {
            'stripe': StripeGateway,
            'paypal': PayPalGateway,
            Payment.STRIPE: StripeGateway,
            Payment.PAYPAL: PayPalGateway,
        }
        
        if gateway_type not in gateways:
            raise ValueError(f"Unsupported payment gateway: {gateway_type}")
        
        return gateways[gateway_type]()
    
    @staticmethod
    def get_gateway_for_payment(payment):
        return PaymentGatewayFactory.get_gateway(payment.payment_option)
    
    @staticmethod
    def get_gateway_for_order(order):
        try:
            payment = Payment.objects.get(order=order)
            return PaymentGatewayFactory.get_gateway(payment.payment_option)
        except Payment.DoesNotExist:
            raise ValueError(f"No payment found for order {order.id}")
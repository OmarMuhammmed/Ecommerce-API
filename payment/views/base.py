from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    """Abstract payment gateway interface"""
    
    @abstractmethod
    def create_checkout_session(self, order):
        """Create a checkout session for the specified order"""
        pass
    
    @abstractmethod
    def process_successful_payment(self, order_id, payment_data):
        """Process a successful payment"""
        pass
    
    @abstractmethod
    def get_payment_option_code(self):
        """Return the payment option code for this gateway"""
        pass
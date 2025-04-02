from django.db import models
from orders.models import Order

class Payment(models.Model):

    PENDING = "P"
    COMPLETED = "C"
    FAILED = "F"


    STATUS_CHOICES = (
        (PENDING, "pending"),
        (COMPLETED, "completed"),
        (FAILED, "failed"),
    )

    PAYPAL = "P"
    STRIPE = "S"
    PAYMENT_CHOICES = (PAYPAL, "paypal"), (STRIPE, "stripe")

    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='p')
    payment_option = models.CharField(max_length=1, choices=PAYMENT_CHOICES)
    order = models.OneToOneField(
        Order, related_name="payment", on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.order.buyer.username

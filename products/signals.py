from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from .models import Product

@receiver(post_save, sender=Product)
def update_search_vector(sender, instance, **kwargs):
    """
    Update search_vector when a product is saved
    """
    # Using update to avoid triggering the signal again
    Product.objects.filter(pk=instance.pk).update(
        search_vector=SearchVector('name', weight='A') + SearchVector('desc', weight='B')
    )
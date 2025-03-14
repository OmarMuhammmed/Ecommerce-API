from django.db import models
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from django.contrib.auth.models import AbstractUser

User = get_user_model()

class CustomUser(AbstractUser):
    is_active = models.BooleanField(default=False)

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    bio = models.CharField(max_length=500, blank=True)
    img = models.ImageField(upload_to='profile_images', blank=True)
    created_at = models.DateTimeField ( auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  
        return f'{self.user.username} Profile'
    
class Address(models.Model):
   
    BILLING = "B"
    SHIPPING = "S"

    ADDRESS_CHOICES = ((BILLING, ("billing")), (SHIPPING, ("shipping")))

    user = models.ForeignKey(User, related_name="address", on_delete=models.CASCADE)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    country = CountryField()
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user.username} Address"    
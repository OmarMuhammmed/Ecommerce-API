from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


def category_image_path(instance, filename):
    return f"product/category/icons/{instance.name}/{filename}"


def product_image_path(instance, filename):
    return f"product/images/{instance.name}/{filename}"


class ProductCategory(models.Model):
    name = models.CharField(max_length=100, db_index=True)  # Add index for faster name lookups
    icon = models.ImageField(upload_to=category_image_path, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Add index for timestamp queries
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = ("Product Category")
        verbose_name_plural = ("Product Categories")

    def __str__(self):
        return self.name


def get_default_product_category():
    return ProductCategory.objects.get_or_create(name="Others")[0]


class Product(models.Model):
    seller = models.ForeignKey(User, related_name="products", on_delete=models.CASCADE, db_index=True)
    category = models.ForeignKey(
        ProductCategory,
        related_name="product_list",
        on_delete=models.SET(get_default_product_category),
        db_index=True
    )
    name = models.CharField(max_length=200, db_index=True)  # Add index for product name searches
    desc = models.TextField(blank=True)
    image = models.ImageField(upload_to=product_image_path, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Add index for timestamp queries
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=['price']),  # Add index for price queries
            models.Index(fields=['quantity']),  # Add index for inventory queries
        ]

    def __str__(self):
        return self.name

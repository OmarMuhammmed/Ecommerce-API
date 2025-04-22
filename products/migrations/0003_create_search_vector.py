from django.db import migrations
from django.contrib.postgres.search import SearchVector

def create_search_vector(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    for product in Product.objects.all():
        product.search_vector = SearchVector('name', weight='A') + SearchVector('desc', weight='B')
        product.save()

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0002_alter_product_created_at_alter_product_name_and_more'),  # Removed the .py extension
    ]

    operations = [
        migrations.RunPython(create_search_vector),
    ]
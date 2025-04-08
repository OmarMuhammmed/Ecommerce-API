from django.urls import path, include
from django.contrib import admin
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView
dj_rest_auth_patterns = [
    path('', include('dj_rest_auth.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # accounts
    path('api/accounts/', include('accounts.urls')),
    path('api/accounts/login/', TokenObtainPairView.as_view()),
    path('api/accounts/', include((dj_rest_auth_patterns, 'dj_rest_auth'), namespace='dj_rest_auth')),  # مع Tag

    # products
    path('api/products/', include('products.urls')),

    # orders
    path('api/orders/', include('orders.urls')),

    # payment
    path('api/payment/', include('payment.urls')),

    # Schema  Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
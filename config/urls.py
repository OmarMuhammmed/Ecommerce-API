from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # accounts
    path('api/accounts/', include('accounts.urls')),
    path('api/accounts/login/', TokenObtainPairView.as_view()),
    path('api/accounts/', include('dj_rest_auth.urls')),

    # products
    path('api/products/', include('products.urls')),

    # orders
    path('api/orders/', include('orders.urls')),

    # payment
    path('api/payment/', include('payment.urls')),

]

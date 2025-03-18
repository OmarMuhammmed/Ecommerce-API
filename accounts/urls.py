from django.urls import path, include 
from .views import RegisterView , ProfileAPIView, AdderssViewSet#, ActivateAccountView
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r"", AdderssViewSet, basename="address")


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path("profile/address/", include(router.urls)),
    
]

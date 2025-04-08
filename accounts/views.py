from rest_framework import  generics
from .serializers import RegisterationSerializer, ProfileSerializer, AddressReadOnlySerializer
from rest_framework.permissions import AllowAny
from django.conf import settings    
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.views import APIView
from accounts.models import CustomUser as User, Profile, Address
from rest_framework.generics import RetrieveUpdateAPIView
from .permissions import IsUserProfileOwner, IsUserAddressOwner
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Accounts'])
class ActivateAccountView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({"message": "Account activated successfully."}, 
                                status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid activation link."}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
        except (User.DoesNotExist, ValueError):
            return Response({"error": "Invalid activation link."}, 
                            status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Accounts'])
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterationSerializer
    permission_classes = [AllowAny]

    def send_activation_email(self, request, user, email):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        current_site = get_current_site(request).domain
        activation_link = f"http://{current_site}/api/accounts/activate/{uid}/{token}/"

        
        subject = "Activate Your Account"
        message = f"Hello {user.username},\n\nPlease activate your account by clicking the link below:\n{activation_link}"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

        return Response({"message": "Registration successful. Please check your email to activate your account."}, 
                        status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        self.send_activation_email(request, user, user.email)
        
        return Response({"message": "Registration successful. Please check your email to activate your account."}, 
                        status=status.HTTP_201_CREATED)

@extend_schema(tags=['Accounts'])
class ProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsUserProfileOwner, IsAuthenticated]
    
    def get_object(self):
        return Profile.objects.select_related('user').get(user=self.request.user)

@extend_schema(tags=['Accounts'])
class AdderssViewSet(ReadOnlyModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressReadOnlySerializer
    permission_classes = [IsUserAddressOwner, IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
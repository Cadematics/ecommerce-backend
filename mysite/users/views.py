from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Address, UserProfile
from .serializers import (
    AddressSerializer, RegisterSerializer, UserProfileSerializer, UserSerializer
)


class RegisterView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = UserSerializer(user).data
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": user_data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# User Profile Views

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Ensure a profile exists for the user, creating one if it doesn't.
        # This is crucial for handling users created before the profile model was introduced.
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retrieve the user's profile and then get all associated addresses.
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile.addresses.all()

    def perform_create(self, serializer):
        # When creating a new address, automatically associate it with the current user's profile.
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        serializer.save(profile=profile)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'  # The field on the model to look up the object by.

    def get_queryset(self):
        # Users should only be able to access and manage their own addresses.
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile.addresses.all()

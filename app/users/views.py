"""
Users API.
"""
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from users.serializers import UserSerializer, LoginSerializer


class SignUpView(generics.CreateAPIView):
    """Register a new user in the system."""

    serializer_class = UserSerializer


class LoginView(TokenObtainPairView):
    """Login a user."""

    serializer_class = LoginSerializer

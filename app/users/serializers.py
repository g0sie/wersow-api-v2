"""
Serializers for users API.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "password", "username"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 6}}
        read_only_fields = ("id",)

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    """Serializer for LoginView."""

    @classmethod
    def get_token(cls, user):
        """Return token with additional email and username data."""
        token = super().get_token(user)

        token["email"] = user.email
        token["username"] = user.username

        return token

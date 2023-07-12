"""
Database models.
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.timezone import now


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, username=None, **extra_fields):
        """Create, save and return a new user."""

        if not email:
            raise ValueError("User must have an email address.")
        if not password:
            raise ValueError("User must have a password.")
        if not username:
            raise ValueError("User must have a username.")

        user = self.model(
            email=self.normalize_email(email), username=username, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, username="admin", **extra_fields):
        """Create, save and return a new superuser."""
        user = self.create_user(
            email=email, password=password, username=username, **extra_fields
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateField(default=now)

    USERNAME_FIELD = "email"

    objects = UserManager()

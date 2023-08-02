"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


def create_user(**params):
    """Helper function for creating users."""
    email = params.pop("email", "test@example.com")
    password = params.pop("password", "testpass123")
    username = params.pop("username", "testusername")

    return get_user_model().objects.create_user(
        email=email, password=password, username=username, **params
    )


class UserModelTests(TestCase):
    """Test User model."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = "test@example.com"
        password = "testpass123"
        username = "testusername"
        user = create_user(email=email, password=password, username=username)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.username, username)

    def test_new_user_is_active(self):
        """Test user is active by default."""
        user = create_user()

        self.assertTrue(user.is_active)

    def test_new_user_is_not_staff(self):
        """Test user is not staff by default."""
        user = create_user()

        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["TEST1@example.com", "TEST1@example.com"],
            ["test2@EXAMPLE.com", "test2@example.com"],
            ["test3@example.COM", "test3@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email, password="testpass123", username="testusername"
            )
            self.assertEqual(user.email, expected)

    def test_create_user_without_email_raises_error(self):
        """Test that creating a user without an email raises ValueError."""
        with self.assertRaises(ValueError):
            create_user(email="")

    def test_create_user_without_password_raises_error(self):
        """Test that creating a user without a password raises ValueError."""
        with self.assertRaises(ValueError):
            create_user(password="")

    def test_create_user_without_username_raises_error(self):
        """Test that creating a user without a username raises ValueError."""
        with self.assertRaises(ValueError):
            create_user(username="")

    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = get_user_model().objects.create_superuser(
            email="admin@example.com", password="testpass123", username="admin"
        )

        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_create_superuser_without_username_successful(self):
        """Test creating a superuser without passing username works."""
        superuser = get_user_model().objects.create_superuser(
            email="admin@example.com", password="testpass123"
        )

        self.assertEqual(superuser.username, "admin")
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

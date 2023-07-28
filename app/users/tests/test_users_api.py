"""
Tests for users API.
"""
import base64
import json

from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status


def create_user(**params):
    """Helper function for creating users."""
    email = params.pop("email", "test@example.com")
    password = params.pop("password", "testpass123")
    username = params.pop("username", "testusername")

    return get_user_model().objects.create_user(
        email=email, password=password, username=username, **params
    )


SIGN_UP_URL = reverse("users:register")
LOG_IN_URL = reverse("users:login")


class AuthenticationTests(TestCase):
    """Tests for user authentication."""

    def setUp(self):
        self.client = Client()

    def test_user_can_sign_up(self):
        """Test user can register to the app."""
        payload = {
            "email": "user@example.com",
            "username": "testuser3000",
            "password": "testpass123",
        }
        res = self.client.post(SIGN_UP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertEqual(user.username, payload["username"])
        self.assertEqual(res.data["id"], user.id)
        self.assertEqual(res.data["email"], user.email)
        self.assertEqual(res.data["username"], user.username)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email already exists."""
        email = "user@example.com"
        create_user(email=email)

        payload = {
            "email": email,
            "username": "testuser3000",
            "password": "testpass123",
        }
        res = self.client.post(SIGN_UP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test error returned if password less than 6 characters."""
        payload = {
            "email": "user@example.com",
            "username": "testuser3000",
            "password": "sh0rt",
        }
        res = self.client.post(SIGN_UP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_user_can_log_in(self):
        """Test user can log in"""
        password = "testpass123"
        user = create_user(password=password)

        payload = {"email": user.email, "password": password}
        res = self.client.post(LOG_IN_URL, payload)

        def parse_data_from_access_token():
            token = res.data["access"]
            header, payload, signature = token.split(".")
            decoded_payload = base64.b64decode(f"{payload}==")
            payload_data = json.loads(decoded_payload)
            return payload_data

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(res.data["refresh"])
        res_data = parse_data_from_access_token()
        self.assertEqual(res_data["user_id"], user.id)
        self.assertEqual(res_data["email"], user.email)
        self.assertEqual(res_data["username"], user.username)

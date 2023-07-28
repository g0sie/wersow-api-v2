"""
Urls for users.
"""
from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users import views

app_name = "users"
urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.SignUpView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

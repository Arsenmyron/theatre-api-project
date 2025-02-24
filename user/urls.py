from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from user.views import CreateUserView, ManageUserView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="user-create"),
    path("token/", TokenObtainPairView.as_view(), name="user-token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="user-token-refresh"),
    path("token/verify", TokenVerifyView.as_view(), name="user-token-verify"),
    path("me/", ManageUserView.as_view(), name="user-manage"),
]

app_name = "user"

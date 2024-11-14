from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenVerifyView

from . import views

app_name = "apps.users"

router = routers.SimpleRouter()
router.register("register", views.UserRegistrationViewSet, basename="register")

urlpatterns = [
    path("", include(router.urls)),
    path("users/activate/<uuid>/<token>/", views.UserActivateView.as_view(), name="activate"),
    path("token", views.TokenObtainPairView().as_view(), name="token_obtain_pair"),
    path("token/refresh", views.TokenRefreshView().as_view(), name="token_refresh"),
    path("token/blacklist/", views.TokenBlacklistView.as_view(), name="token_blacklist"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

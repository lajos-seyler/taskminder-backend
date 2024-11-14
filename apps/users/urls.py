from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "apps.users"

router = routers.SimpleRouter()
router.register("register", views.UserRegistrationViewSet, basename="register")

urlpatterns = [
    path("", include(router.urls)),
    path("users/activate/<uuid>/<token>/", views.UserActivateView.as_view(), name="activate"),
    path("users/token", views.TokenObtainPairView().as_view(), name="token_obtain_pair"),
]

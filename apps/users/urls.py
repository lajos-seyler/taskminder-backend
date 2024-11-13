from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "apps.users"

router = routers.SimpleRouter()
router.register("register", views.UserRegistrationViewSet, basename="register")

urlpatterns = [
    path("", include(router.urls)),
]
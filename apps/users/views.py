from rest_framework.viewsets import ModelViewSet

from .models import User
from .serializers import UserRegistrationSerializer
from .utils import send_registration_email


class UserRegistrationViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = []
    http_method_names = ["post"]

    def perform_create(self, serializer):
        user = serializer.save()
        send_registration_email(user)

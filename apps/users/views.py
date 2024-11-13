from rest_framework.viewsets import ModelViewSet

from .models import User
from .serializers import UserRegistrationSerializer


class UserRegistrationViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = []
    http_method_names = ["post"]

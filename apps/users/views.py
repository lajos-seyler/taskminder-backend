from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
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


class UserActivateView(APIView):
    def get(self, *args, uuid, token):
        user = get_object_or_404(User, uuid=uuid)

        if not user.activate(token):
            return Response({"message": "Invalid or expired activation token."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "User activated successfully."}, status=status.HTTP_200_OK)

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenBlacklistView as DefaultTokenBlacklistView
from rest_framework_simplejwt.views import TokenObtainPairView as DefaultTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView as DefaultTokenRefreshView

from .models import User
from .serializers import TokenObtainPairSerializer, UserRegistrationSerializer
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


class TokenObtainPairView(DefaultTokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.pop("refresh", None)
        response.set_cookie(
            key="refresh",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="None",
        )
        return response


class TokenRefreshView(DefaultTokenRefreshView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh", None)
        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenBlacklistView(DefaultTokenBlacklistView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh", None)
        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        response.delete_cookie("refresh")
        return response

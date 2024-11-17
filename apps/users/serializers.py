from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as DefaultTokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "uuid",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "date_joined",
        )
        read_only_fields = ("id", "uuid", "is_staff", "is_active", "date_joined")
        extra_kwargs = {
            "username": {"required": True},
            "email": {"required": True},
            "password": {"required": True, "write_only": True},
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TokenObtainPairSerializer(DefaultTokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["email"] = user.email
        return token

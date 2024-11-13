from rest_framework import serializers

from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "date_joined",
        )
        read_only_fields = ("id", "is_staff", "is_active", "date_joined")
        extra_kwargs = {
            "username": {"required": True},
            "email": {"required": True},
            "password": {"required": True, "write_only": True},
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models, transaction
from django.utils import timezone

from .tokens import account_activation_token


class UserManager(BaseUserManager):
    use_in_migrations = True

    @transaction.atomic
    def _create_user(self, username, email, password, **extra_fields):
        email = self.normalize_email(email)
        fields = {**extra_fields, "email": email}
        if username is not None:
            fields["username"] = username
        user = self.model(**fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")  # noqa: EM101
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")  # noqa: EM101

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    username = models.CharField(unique=True, max_length=50)
    email = models.EmailField(blank=False, unique=True)
    first_name = models.CharField(blank=True, max_length=128)
    last_name = models.CharField(blank=True, max_length=128)
    is_staff = models.BooleanField(default=False, help_text="The user can access the admin site")
    is_active = models.BooleanField(default=False, help_text="The user account is active")
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_activation_token(self):
        return account_activation_token.make_token(self)

    def get_activation_link(self):
        return f"{settings.FRONTEND_URL}/users/activate/{self.pk}/{self.get_activation_token()}"

    def __str__(self):
        return f"User username={self.username} email={self.email}"

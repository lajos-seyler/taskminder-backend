from factory import (
    Faker,
)
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from apps.users.models import User


class UserFactory(DjangoModelFactory):
    username = FuzzyText()
    email = FuzzyText(suffix="@example.com")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    password = FuzzyText(length=8)

    is_active = True

    class Meta:
        model = User

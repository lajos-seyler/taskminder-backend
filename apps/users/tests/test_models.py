import pytest
from django.db import transaction

from apps.users.models import User

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "create_func,exp_staff,exp_superuser,exp_is_active",
    [
        [User.objects.create_user, False, False, False],
        [User.objects.create_superuser, True, True, True],
    ],
)
@pytest.mark.parametrize("password", [None, "pass"])
def test_create_user(create_func, exp_staff, exp_superuser, exp_is_active, password):
    username = "user1"
    email = "user@example.com"
    first_name = "Jane"
    last_name = "Doe"

    with transaction.atomic():
        user = create_func(username, email=email, first_name=first_name, last_name=last_name, password=password)

    assert user.username == username
    assert user.email == email
    assert user.first_name == first_name
    assert user.last_name == last_name
    assert user.get_full_name() == f"{first_name} {last_name}"
    assert user.is_staff is exp_staff
    assert user.is_superuser is exp_superuser
    assert user.is_active is exp_is_active

    if password is not None:
        assert user.check_password(password)

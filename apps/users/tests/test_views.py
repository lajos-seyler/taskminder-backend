import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.users.factories import UserFactory

User = get_user_model()


pytestmark = pytest.mark.django_db

REGISTER_URL = reverse("apps.users:register-list")
TOKEN_URL = reverse("apps.users:token_obtain_pair")
REFRESH_URL = reverse("apps.users:token_refresh")
BLACKLIST_URL = reverse("apps.users:token_blacklist")


@pytest.mark.parametrize(
    "username, email, first_name, last_name, password",
    [
        ["user1", "user1@example.com", "Jane", "Doe", "pass"],
        ["user2", "user2@example.com", "John", "Smith", "pass"],
    ],
)
def test_user_registration_view(drf_client, username, email, first_name, last_name, password):
    data = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
    }

    response = drf_client.post(REGISTER_URL, data, format="json")

    assert response.status_code == 201
    assert response.data["username"] == username
    assert response.data["email"] == email
    assert response.data["first_name"] == first_name
    assert response.data["last_name"] == last_name
    assert response.data["is_staff"] is False
    assert response.data["is_active"] is False
    assert "password" not in response.data
    assert "date_joined" in response.data
    assert "id" in response.data


def test_user_registration_view_invalid_data(drf_client):
    data = {
        "username": "",
        "email": "",
        "first_name": "",
        "last_name": "",
        "password": "",
    }

    response = drf_client.post(REGISTER_URL, data, format="json")

    assert response.status_code == 400
    assert "username" in response.data
    assert "email" in response.data
    assert "password" in response.data
    assert "first_name" not in response.data
    assert "last_name" not in response.data
    assert "non_field_errors" not in response.data
    assert "is_staff" not in response.data
    assert "is_active" not in response.data
    assert "date_joined" not in response.data
    assert "id" not in response.data


def test_user_registration_view_method_not_allowed(drf_client):
    response = drf_client.get(REGISTER_URL)

    assert response.status_code == 405
    assert response.data == {"detail": 'Method "GET" not allowed.'}
    assert response["Allow"] == "POST"


def test_user_activate_view(drf_client):
    user_data = UserFactory.build()

    data = {
        "username": user_data.username,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "password": user_data.password,
    }

    response = drf_client.post(REGISTER_URL, data, format="json")
    registered_user = User.objects.get(id=response.json()["id"])

    assert registered_user.is_active is False

    activate_url = reverse(
        "apps.users:activate", kwargs={"uuid": registered_user.uuid, "token": registered_user.get_activation_token()}
    )
    response = drf_client.get(activate_url, follow=True)
    registered_user.refresh_from_db()

    assert response.status_code == 200
    assert response.data["message"] == "User activated successfully."
    assert registered_user.is_active is True


def test_user_activate_view_invalid_token(drf_client):
    user_data = UserFactory.build()

    data = {
        "username": user_data.username,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "password": user_data.password,
    }

    response = drf_client.post(REGISTER_URL, data, format="json")
    registered_user = User.objects.get(id=response.json()["id"])

    assert registered_user.is_active is False

    activate_url = reverse(
        "apps.users:activate",
        kwargs={"uuid": registered_user.uuid, "token": "invalid_token"},
    )
    response = drf_client.get(activate_url, follow=True)
    registered_user.refresh_from_db()

    assert response.status_code == 400
    assert response.data["message"] == "Invalid or expired activation token."
    assert registered_user.is_active is False


def test_token_obtain_pair_view(drf_client, user):
    new_user = UserFactory.create()
    new_user.set_password(user.password)
    new_user.save()

    data = {
        "email": new_user.email,
        "password": user.password,
    }

    response = drf_client.post(TOKEN_URL, data, format="json")

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" not in response.data


def test_token_obtain_pair_view_invalid_credentials(drf_client):
    data = {
        "email": "invalid@example.com",
        "password": "password123",
    }

    response = drf_client.post(TOKEN_URL, data, format="json")

    assert response.status_code == 401
    assert "access" not in response.data
    assert response.data["detail"] == "No active account found with the given credentials"


def test_token_refresh_view(drf_client, user):
    new_user = UserFactory.create(password=user.password)

    data = {
        "email": new_user.email,
        "password": user.password,
    }

    response = drf_client.post(TOKEN_URL, data, format="json")
    assert response.status_code == 200

    refresh_token = response.cookies.get("refresh")
    assert refresh_token is not None

    drf_client.cookies["refresh"] = refresh_token

    response = drf_client.post(REFRESH_URL)

    assert response.status_code == 200
    assert "access" in response.data


def test_token_refresh_view_no_token(drf_client):
    response = drf_client.post(REFRESH_URL)

    assert response.status_code == 400
    assert response.data["refresh"][0] == "This field may not be null."
    assert "access" not in response.data


def test_token_refresh_view_with_invalid_token(drf_client):
    drf_client.cookies["refresh"] = "invalid_token"
    response = drf_client.post(REFRESH_URL)

    assert response.status_code == 401
    assert response.data["detail"] == "Token is invalid or expired"
    assert "access" not in response.data


def test_token_blacklist_view(drf_client, user):
    new_user = UserFactory.create(password=user.password)

    data = {
        "email": new_user.email,
        "password": user.password,
    }

    response = drf_client.post(TOKEN_URL, data, format="json")
    assert response.status_code == 200

    refresh_token = response.cookies.get("refresh")
    assert refresh_token is not None

    drf_client.cookies["refresh"] = refresh_token

    response = drf_client.post(BLACKLIST_URL, format="json")
    assert response.status_code == 200

    # Check if cookie is deleted in response
    response = drf_client.post(REFRESH_URL)
    assert response.status_code == 400
    assert response.data["refresh"][0] == "This field may not be blank."

    # Check if re-using the same refresh token is not possible
    drf_client.cookies["refresh"] = refresh_token
    response = drf_client.post(REFRESH_URL)
    assert response.status_code == 401
    assert response.data["detail"] == "Token is blacklisted"


def test_token_blacklist_view_with_invalid_token(drf_client):
    drf_client.cookies["refresh"] = "invalid_token"

    response = drf_client.post(BLACKLIST_URL, format="json")
    assert response.status_code == 401
    assert response.data["detail"] == "Token is invalid or expired"

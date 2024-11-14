import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.users.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, email, first_name, last_name, password",
    [
        ["user1", "user1@example.com", "Jane", "Doe", "pass"],
        ["user2", "user2@example.com", "John", "Smith", "pass"],
    ],
)
def test_user_registration_view(drf_client, username, email, first_name, last_name, password):
    url = "/api/register/"

    data = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
    }

    response = drf_client.post(url, data, format="json")

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


@pytest.mark.django_db
def test_user_registration_view_invalid_data(drf_client):
    url = "/api/register/"
    data = {
        "username": "",
        "email": "",
        "first_name": "",
        "last_name": "",
        "password": "",
    }

    response = drf_client.post(url, data, format="json")

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


@pytest.mark.django_db
def test_user_registration_view_method_not_allowed(drf_client):
    url = "/api/register/"

    response = drf_client.get(url)

    assert response.status_code == 405
    assert response.data == {"detail": 'Method "GET" not allowed.'}
    assert response["Allow"] == "POST"


@pytest.mark.django_db
def test_user_activate_view(drf_client):
    register_url = "/api/register/"

    user_data = UserFactory.build()

    data = {
        "username": user_data.username,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "password": user_data.password,
    }

    response = drf_client.post(register_url, data, format="json")
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


@pytest.mark.django_db
def test_user_activate_view_invalid_token(drf_client):
    register_url = "/api/register/"

    user_data = UserFactory.build()

    data = {
        "username": user_data.username,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "password": user_data.password,
    }

    response = drf_client.post(register_url, data, format="json")
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

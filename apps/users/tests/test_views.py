import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, email, first_name, last_name, password",
    [
        ["user1", "user1@example.com", "Jane", "Doe", "pass"],
        ["user2", "user2@example.com", "John", "Smith", "pass"],
    ],
)
def test_user_registration_view(username, email, first_name, last_name, password):
    client = APIClient()
    url = "/api/register/"

    data = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
    }

    response = client.post(url, data, format="json")

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
def test_user_registration_view_invalid_data():
    client = APIClient()
    url = "/api/register/"

    data = {
        "username": "",
        "email": "",
        "first_name": "",
        "last_name": "",
        "password": "",
    }

    response = client.post(url, data, format="json")

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
def test_user_registration_view_method_not_allowed():
    client = APIClient()
    url = "/api/register/"

    response = client.get(url)

    assert response.status_code == 405
    assert response.data == {"detail": 'Method "GET" not allowed.'}
    assert response["Allow"] == "POST"

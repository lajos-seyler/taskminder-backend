import pytest
from django.urls import reverse

from apps.tasks.factories import FolderFactory
from apps.tasks.models import Folder
from apps.tasks.serializers import FolderSerializer
from apps.users.factories import UserFactory

pytestmark = pytest.mark.django_db


FOLDERS_URL = reverse("apps.tasks:folders-list")


def test_get_folders(user, user_drf_client):
    other_user = UserFactory()

    FolderFactory.create_batch(3, owner=user)
    FolderFactory.create_batch(3, owner=other_user)

    response = user_drf_client.get(FOLDERS_URL)

    assert response.status_code == 200
    print(response.data)
    assert len(response.data["results"]) == 3


def test_post_folder(user, user_drf_client):
    folders = FolderFactory.build_batch(3, owner=user)

    for folder in folders:
        serializer = FolderSerializer(folder)
        response = user_drf_client.post(FOLDERS_URL, serializer.data, format="json")
        assert response.status_code == 201

    assert user.folders.count() == 3


def test_patch_folder(user, user_drf_client):
    folder = FolderFactory.create(owner=user)
    folder_url = reverse("apps.tasks:folders-detail", kwargs={"pk": folder.id})
    data = {"name": "patched_folder"}

    response = user_drf_client.patch(folder_url, data)

    assert response.status_code == 200
    assert response.data["name"] == data["name"]

    folder.refresh_from_db()
    assert folder.name == data["name"]


def test_delete_folder(user, user_drf_client):
    folders = FolderFactory.create_batch(3, owner=user)

    folder_to_delete = folders[0]
    folder_url = reverse("apps.tasks:folders-detail", kwargs={"pk": folder_to_delete.id})

    response = user_drf_client.delete(folder_url)

    assert response.status_code == 204

    with pytest.raises(Folder.DoesNotExist):
        folder_to_delete.refresh_from_db()


def test_get_other_users_folder_raises_error(user_drf_client):
    other_user = UserFactory()
    other_user_folder = FolderFactory(owner=other_user)
    other_user_folder_url = reverse("apps.tasks:folders-detail", kwargs={"pk": other_user_folder.id})

    response = user_drf_client.get(other_user_folder_url)

    assert response.status_code == 404


def test_delete_other_users_folder_raises_error(user_drf_client):
    other_user = UserFactory()
    other_user_folder = FolderFactory(owner=other_user)
    other_user_folder_url = reverse("apps.tasks:folders-detail", kwargs={"pk": other_user_folder.id})

    response = user_drf_client.delete(other_user_folder_url)

    assert response.status_code == 404


def test_create_folder_owner_field_is_readonly(user, user_drf_client):
    other_user = UserFactory()
    data = {"owner": other_user.id, "name": "test"}

    response = user_drf_client.post(FOLDERS_URL, data, format="json")

    assert response.status_code == 201

    created_folder = Folder.objects.get(pk=response.data["id"])
    assert created_folder.owner.id == user.id

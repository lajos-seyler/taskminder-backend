import pytest
from django.urls import reverse

from apps.tasks.factories import TagFactory
from apps.tasks.models import Tag
from apps.tasks.serializers import TagSerializer
from apps.users.factories import UserFactory

pytestmark = pytest.mark.django_db


TAGS_URL = reverse("apps.tasks:tags-list")


def test_get_tags(user, user_drf_client):
    other_user = UserFactory()

    TagFactory.create_batch(3, owner=user)
    TagFactory.create_batch(3, owner=other_user)

    response = user_drf_client.get(TAGS_URL)

    assert response.status_code == 200
    assert len(response.data["results"]) == 3


def test_post_tag(user, user_drf_client):
    tags = TagFactory.build_batch(3, owner=user)

    for tag in tags:
        serializer = TagSerializer(tag)
        response = user_drf_client.post(TAGS_URL, serializer.data, format="json")
        assert response.status_code == 201

    assert user.tags.count() == 3


def test_patch_tag(user, user_drf_client):
    tag = TagFactory.create(owner=user)
    tag_url = reverse("apps.tasks:tags-detail", kwargs={"pk": tag.id})
    data = {"name": "patched_tag"}

    response = user_drf_client.patch(tag_url, data)

    assert response.status_code == 200
    assert response.data["name"] == data["name"]

    tag.refresh_from_db()
    assert tag.name == data["name"]


def test_delete_tag(user, user_drf_client):
    tags = TagFactory.create_batch(3, owner=user)

    tag_to_delete = tags[0]
    tag_url = reverse("apps.tasks:tags-detail", kwargs={"pk": tag_to_delete.id})

    response = user_drf_client.delete(tag_url)

    assert response.status_code == 204

    with pytest.raises(Tag.DoesNotExist):
        tag_to_delete.refresh_from_db()


def test_get_other_users_tag_raises_error(user_drf_client):
    other_user = UserFactory()
    other_user_tag = TagFactory(owner=other_user)
    other_user_tag_url = reverse("apps.tasks:tags-detail", kwargs={"pk": other_user_tag.id})

    response = user_drf_client.get(other_user_tag_url)

    assert response.status_code == 404


def test_delete_other_users_tag_raises_error(user_drf_client):
    other_user = UserFactory()
    other_user_tag = TagFactory(owner=other_user)
    other_user_tag_url = reverse("apps.tasks:tags-detail", kwargs={"pk": other_user_tag.id})

    response = user_drf_client.delete(other_user_tag_url)

    assert response.status_code == 404


def test_create_tag_owner_field_is_readonly(user, user_drf_client):
    other_user = UserFactory()
    data = {"owner": other_user.id, "name": "test"}

    response = user_drf_client.post(TAGS_URL, data, format="json")

    assert response.status_code == 201

    created_tag = Tag.objects.get(pk=response.data["id"])
    assert created_tag.owner.id == user.id

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.tasks.factories import FolderFactory, ProjectFactory, TagFactory, TaskFactory
from apps.users.factories import UserFactory

pytestmark = pytest.mark.django_db


TASKS_URL = reverse("apps.tasks:tasks-list")


def test_get_tasks(user, user_drf_client):
    other_user = UserFactory()

    TaskFactory.create_batch(3, owner=user)
    TaskFactory.create_batch(4, owner=other_user)

    response = user_drf_client.get(TASKS_URL)

    assert response.status_code == 200
    assert len(response.data) == 3


@pytest.mark.parametrize(
    "title, text, has_folder, has_project, has_tags",
    [
        ["test task 1", "", False, False, False],
        ["test task 2", "", True, False, False],
        ["test task 3", "", False, True, False],
        ["test task 4", "text 4", False, False, True],
        ["test task 5", "text 5", True, True, True],
    ],
)
def test_post_task(user, user_drf_client, title, text, has_folder, has_project, has_tags):
    folder = FolderFactory(owner=user).id if has_folder else None
    project = ProjectFactory(owner=user).id if has_project else None
    tags = [tag.id for tag in TagFactory.create_batch(3, owner=user)] if has_tags else []

    data = {
        "title": title,
        "text": text,
        "folder": folder,
        "project": project,
        "tags": tags,
    }

    # Filter out keys where the value is None or an empty string
    data = {key: value for key, value in data.items() if value not in (None, "")}

    if folder and project:
        with pytest.raises(ValidationError):
            user_drf_client.post(TASKS_URL, data, format="json")

    else:
        response = user_drf_client.post(TASKS_URL, data, format="json")

        assert response.status_code == 201
        assert response.data["title"] == data["title"]
        assert response.data["text"] == data.get("text", "")
        assert response.data["folder"] is None if folder is None else response.data["folder"] == folder
        assert response.data["project"] is None if project is None else response.data["project"] == project
        assert response.data["tags"] == tags


@pytest.mark.parametrize(
    "rrule_params, expected_occurrences_count",
    [
        [{"freq": "DAILY"}, 1],
        [{"freq": "DAILY", "interval": 2, "count": 12}, 12],
        [{"freq": "MONTHLY", "interval": 3, "count": 6, "bymonthday": [5, 10, 15]}, 6],
    ],
)
def test_post_task_with_rrule_params(user, user_drf_client, rrule_params, expected_occurrences_count):
    data = {
        "title": "test task",
        "start_time": "2024-11-19T14:00:00",
        "end_time": "2024-11-19T16:00:00",
        "rrule_params": rrule_params,
    }

    response = user_drf_client.post(TASKS_URL, data, format="json")

    assert response.status_code == 201

    task = user.tasks.filter(pk=response.data["id"])
    assert task.exists() is True
    assert task[0].occurrences.count() == expected_occurrences_count

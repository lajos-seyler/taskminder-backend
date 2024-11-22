import pytest

from apps.tasks.factories import FolderFactory, OccurrenceFactory, ProjectFactory, TagFactory, TaskFactory

pytestmark = pytest.mark.django_db


def test_task_str_representation():
    task = TaskFactory()

    assert str(task) == f"{task.title} (id={task.id})"


def test_folder_str_representation():
    folder = FolderFactory()

    assert str(folder) == folder.name


def test_project_str_representation():
    folder = FolderFactory()
    project_with_folder = ProjectFactory(folder=folder)
    project_without_folder = ProjectFactory(folder=None)

    assert str(project_with_folder) == f"{project_with_folder.folder.name}/{project_with_folder.name}"
    assert str(project_without_folder) == f"{project_without_folder.name}"


def test_tag_str_representation():
    tag = TagFactory()

    assert str(tag) == tag.name


def test_occurrence_str_representation():
    occurrence = OccurrenceFactory()

    assert str(occurrence) == f"{occurrence.task.title}: {occurrence.start_time}"

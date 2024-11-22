from datetime import timedelta, timezone

import factory
import faker
from factory.django import DjangoModelFactory

from apps.users.factories import UserFactory

from .models import Folder, Occurrence, Project, Tag, Task


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Faker("word")
    owner = factory.SubFactory(UserFactory)


class FolderFactory(DjangoModelFactory):
    class Meta:
        model = Folder

    name = factory.Faker("word")
    owner = factory.SubFactory(UserFactory)


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Faker("word")
    folder = factory.SubFactory(FolderFactory)
    owner = factory.SubFactory(UserFactory)


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task
        skip_postgeneration_save = True

    title = factory.Faker("sentence", nb_words=4)
    text = factory.Faker("paragraph")
    owner = factory.SubFactory(UserFactory)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)

    @factory.post_generation
    def set_folder_or_project(obj, create, extracted, **kwargs):
        if not create:
            return

        faker = factory.Faker._get_faker()
        choice = faker.random_element(elements=["project", "folder", None])

        if choice == "project":
            obj.project = ProjectFactory()
        elif choice == "folder":
            obj.folder = FolderFactory()

        obj.save()

    owner = factory.SubFactory(UserFactory)


class OccurrenceFactory(DjangoModelFactory):
    class Meta:
        model = Occurrence

    start_time = factory.Faker("date_time", tzinfo=timezone.utc)
    end_time = factory.LazyAttribute(lambda o: o.start_time + timedelta(hours=faker.Faker().random_int(min=1, max=5)))
    task = factory.SubFactory(TaskFactory)

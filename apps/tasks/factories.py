from datetime import timezone

import factory
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
    folder = factory.Maybe(factory.Faker("boolean", chance_of_getting_true=50), factory.SubFactory(FolderFactory), None)
    project = factory.Maybe(
        factory.Faker("boolean", chance_of_getting_true=50), factory.SubFactory(ProjectFactory), None
    )
    owner = factory.SubFactory(UserFactory)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class OccurrenceFactory(DjangoModelFactory):
    class Meta:
        model = Occurrence

    start_time = factory.Faker("date_time", tzinfo=timezone.utc)
    end_time = factory.LazyAttribute(lambda obj: obj.start_time + factory.Faker("time_delta").generate())
    task = factory.SubFactory(TaskFactory)

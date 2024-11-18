from datetime import timezone

from dateutil import rrule
from django.core.exceptions import ValidationError
from django.db import models

from apps.users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=63)
    owner = models.ForeignKey(User, related_name="tags", on_delete=models.CASCADE)

    class Meta:
        unique_together = [["name", "owner"]]

    def __str__(self):
        return self.name


class Folder(models.Model):
    name = models.CharField(max_length=63)
    owner = models.ForeignKey(User, related_name="folders", on_delete=models.CASCADE)

    class Meta:
        unique_together = [["name", "owner"]]

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=63)
    folder = models.ForeignKey(Folder, related_name="projects", null=True, blank=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey(User, related_name="projects", on_delete=models.CASCADE)

    def __str__(self):
        folder_path = f"{self.folder}/" if self.folder else ""
        return f"{folder_path}{self.name}"


class Task(models.Model):
    title = models.CharField(max_length=63)
    text = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, related_name="tasks", blank=True)
    folder = models.ForeignKey(Folder, related_name="tasks", null=True, blank=True, on_delete=models.SET_NULL)
    project = models.ForeignKey(Project, related_name="tasks", null=True, blank=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey(User, related_name="tasks", on_delete=models.CASCADE)

    def clean(self):
        if self.project and self.folder:
            raise ValidationError("A Task cannot be linked to both a Project and a Folder.")
        if not self.project and not self.folder:
            raise ValidationError("A Task must be linked to either a Project or a Folder.")

    def __str__(self):
        return f"{self.title} (id={self.id})"

    def add_occurrences(self, start_time, end_time, **rrule_params):
        start_time = start_time.replace(tzinfo=timezone.utc)
        end_time = end_time.replace(tzinfo=timezone.utc)
        count = rrule_params.get("count")
        until = rrule_params.get("until")

        if not (count or until):
            self.occurrences.create(start_time=start_time, end_time=end_time)
        else:
            rrule_params.setdefault("freq", rrule.DAILY)
            duration = end_time - start_time
            occurrences = []
            for occurrence_datetime in rrule.rrule(dtstart=start_time, **rrule_params):
                occurrences.append(
                    Occurrence(
                        start_time=occurrence_datetime,
                        end_time=occurrence_datetime + duration,
                        task=self,
                    )
                )
            self.occurrences.bulk_create(occurrences)


class Occurrence(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    task = models.ForeignKey(Task, related_name="occurrences", editable=False, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.event.title, self.start_time)

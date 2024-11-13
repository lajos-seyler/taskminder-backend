import django
from django.contrib.admin import models


class LogEntryManager(models.LogEntryManager):
    """The default LogEntry Model Manager."""

    def __init__(self, model=None):
        super().__init__()
        self.model = model
        if django.VERSION >= (5, 1):
            # Prevent RemovedInDjango60Warning by reverting deprecated method
            type(self).log_action = models.LogEntryManager.log_action


class NoLogEntryManager(LogEntryManager):
    """A No LogEntry Model Manager."""

    # Deprecated in Django 5.1 to be removed in Django 6.0
    def log_action(self, *args, **kwargs):
        return None

    def log_actions(self, *args, **kwargs):
        # No logging
        return None

    def get_queryset(self):
        # No queries
        return super().get_queryset().none()

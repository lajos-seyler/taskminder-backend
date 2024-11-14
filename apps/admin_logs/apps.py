from django.apps import AppConfig


class AdminLogsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.admin_logs"

    def ready(self):
        # Import models after apps loaded to avoid AppRegistryNotReady exception
        from django.contrib.admin.models import LogEntry

        from .models import NoLogEntryManager

        # Switch to the model manager that doesn't log
        LogEntry.objects = NoLogEntryManager(LogEntry)

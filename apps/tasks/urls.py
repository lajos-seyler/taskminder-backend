from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "apps.tasks"

router = routers.SimpleRouter()
router.register("folders", views.FolderViewSet, basename="folders")
router.register("projects", views.ProjectViewSet, basename="projects")
router.register("tags", views.TagViewSet, basename="tags")
router.register("tasks", views.TasksViewSet, basename="tasks")

urlpatterns = [
    path("", include(router.urls)),
]

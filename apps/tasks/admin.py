from django.contrib import admin

from .models import Folder, Occurrence, Project, Tag, Task

admin.site.register(Tag)
admin.site.register(Folder)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Occurrence)

from django.contrib import admin

from . models import Project,AssignedProjects,Task

# Register your models here.

admin.site.register(Project)

admin.site.register(AssignedProjects)

admin.site.register(Task)
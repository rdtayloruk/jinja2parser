from django.contrib import admin
from django.contrib.auth.models import User

from .models import Project

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','url')
    fields = ('name', 'url', 'template_def', 'slug','webhook_key')
    readonly_fields = ('webhook_key',)
    

admin.site.register(Project, ProjectAdmin)

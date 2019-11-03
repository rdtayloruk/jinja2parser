from django.contrib import admin
from django.contrib.auth.models import User

from .models import Project, Version

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','url')
    fields = ('name', 'url', 'template_def', 'slug','webhook_key')
    readonly_fields = ('slug', 'webhook_key')

class VersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'hexsha', 'committed_date')
    fields = ('name', 'project', 'hexsha', 'committed_date')
    readonly_fields = ('name', 'project','hexsha', 'committed_date')
    

admin.site.register(Project, ProjectAdmin)
admin.site.register(Version, VersionAdmin)

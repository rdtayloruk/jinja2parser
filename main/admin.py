from django.contrib import admin
from django.contrib.auth.models import User

from .models import Project, Version, Template, VarFile

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','url')
    fields = ('name', 'url', 'template_def', 'slug','webhook_key')
    readonly_fields = ('slug', 'webhook_key')

class VersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'hexsha', 'committed_date')
    list_filter = ('project__name',)
    fields = ('name', 'project', 'hexsha', 'committed_date', 'slug', 'version_path')
    readonly_fields = ('name', 'project','hexsha', 'committed_date', 'slug','version_path')

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'project')
    list_filter = ('version__project__name',)
    fields = ('name', 'path', 'version')
    readonly_fields = ('name', 'path', 'version')
    
    def project(self, obj):
        return obj.version.project.name
    
    

admin.site.register(Project, ProjectAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Template, TemplateAdmin)

from django.contrib import admin
from django.contrib.auth.models import User

from .models import Project, Version, Template, VarFile

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','url')
    fields = ('name', 'url', 'template_def', 'provider', 'slug','webhook_key', 'webhook_url')
    readonly_fields = ('slug', 'webhook_key', 'webhook_url')

class VersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'hexsha', 'committed_date')
    list_filter = ('project__name',)
    fields = ('name', 'project', 'hexsha', 'committed_date', 'slug', 'path')
    readonly_fields = ('name', 'project','hexsha', 'committed_date', 'slug','path')

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'version', 'project')
    list_filter = ('version__project__name',)
    fields = ('name', 'description', 'template', 'version')
    readonly_fields = ('name', 'description', 'template', 'version')
    
    def project(self, obj):
        return obj.version.project.name

class VarFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'template', 'version', 'project')
    list_filter = ('template__version__project__name', 'template__version__name', 'template__name',)
    fields = ('name', 'description', 'varfile', 'template')
    readonly_fields = ('name', 'description', 'varfile', 'template')
    
    def version(self, obj):
        return obj.template.version.name
    
    def project(self, obj):
        return obj.template.version.project.name
    
    

admin.site.register(Project, ProjectAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Template, TemplateAdmin)
admin.site.register(VarFile, VarFileAdmin)
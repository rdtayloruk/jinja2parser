from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('convert', views.convert, name='convert'),
    path('projects/<int:project_id>/versions', views.project_versions, name='project_versions'),
    path('versions/<int:version_id>/templates', views.version_templates, name='version_templates'),
    path('templates/<int:template_id>/varfiles', views.template_varfiles, name='template_varfiles'),
    path('webhook/project/<project_slug>', views.webhook, name='webhook'),
]
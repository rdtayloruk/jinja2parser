from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('convert', views.convert, name='convert'),
    path('projects/<project_id>/versions', views.project_versions, name='project_versions'),
    path('versions/<version_id>/templates', views.version_templates, name='version_templates'),
    path('templates/<template_id>/varfiles', views.template_varfiles, name='template_varfiles'),
]
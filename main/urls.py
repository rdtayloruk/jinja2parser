from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('convert', views.convert, name='convert'),
    path('projects/<project_slug>/versions', views.project_versions, name='project_versions'),
    path('projects/<project_slug>/versions/<version_slug>/templates', views.version_templates, name='version_templates'),
    path('projects/<project_slug>/versions/<version_slug>/templates/<template_slug>/varfiles', views.template_varfiles, name='template_varfiles'),
    #path('repos/<owner>/<repo>/contents/<path>', views.repo_file, name='repo_file'),
]
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('convert', views.convert, name='convert'),
    path('projects/<project_name>/versions', views.project_versions, name='project_versions'),
    path('projects/<project_name>/versions/<version_name>/templates', views.versions_templates, name='version_templates'),
    path('projects/<project_name>/versions/<version_name>/templates/<template_name>/varfiles', views.template_varfiles, name='template_varfiles'),
    #path('repos/<owner>/<repo>/contents/<path>', views.repo_file, name='repo_file'),
]
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('convert', views.convert, name='convert'),
    #path('repos/<owner>/<repo>/templates', views.repo_template_list, name='repo_templates_list'),
    #path('repos/<owner>/<repo>/contents/<path>', views.repo_file, name='repo_file'),
]
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('convert', views.convert, name='convert'),
    path('templateList', views.template_list, name='template_list'),
    path('template', views.template, name='template'),
]
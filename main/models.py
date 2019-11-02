import os
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.conf import settings


class Project(models.Model):
    name = models.CharField(verbose_name="Project Name", max_length=200 )
    slug = models.SlugField(verbose_name="Slug", unique=True)
    url = models.URLField(verbose_name="Project URL")
    template_def = models.CharField(verbose_name="Jinja2 Definition File", max_length=200 )
    webhook_key = models.CharField(verbose_name="Webhook Key", max_length=200)
    
    @property
    def project_path(self):
        return os.path.join(settings.MEDIA_ROOT, 'projects', self.slug.replace('_', '-'))
    
    @property
    def working_dir(self):
        return os.path.join(self.project_path, 'checkout')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if not self.webhook_key:
            self.webhook_key = get_random_string(length=25)
        super().save(*args, **kwargs)
    
class Version(models.Model):
    hexsha = models.CharField(max_length=200, unique=True)
    committed_date = models.DateTimeField()
    name = models.CharField(max_length=200)
    templates_dir = models.CharField(max_length=200)
    vars_dir = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name = 'versions')
    
    def __str__(self):
        return self.name

class Template(models.Model):
    name = models.CharField(max_length=200)
    path = models.FileField(upload_to=None)
    version = models.ForeignKey(Version, on_delete=models.CASCADE, related_name = 'templates')
    
    def __str__(self):
        return self.name
    
class VarFile(models.Model):
    name = models.CharField(max_length=200)
    path = models.FileField(upload_to=None)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name = 'varfiles')
    
    def __str__(self):
        return self.name
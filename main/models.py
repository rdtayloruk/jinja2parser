import os, re
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse
from main.build import Repo


class Project(models.Model):
    name = models.CharField(verbose_name="Project Name", max_length=200,
                            unique=True)
    slug = models.SlugField(verbose_name="Slug", unique=True)
    url = models.URLField(verbose_name="Project URL")
    template_def = models.CharField(verbose_name="Jinja2 Definition File",
                                    max_length=200)
    webhook_key = models.CharField(verbose_name="Webhook Key", max_length=200)
    
    @property
    def project_rel_path(self):
        return os.path.join('projects', 
                            self.slug.replace('_', '-'))
    
    @property
    def project_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.project_rel_path)
    
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
    name = models.CharField(max_length=200)
    slug = models.SlugField(verbose_name="Slug")
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                related_name = 'versions')
    hexsha = models.CharField(max_length=200)
    committed_date = models.DateTimeField()
    
    @property
    def version_rel_path(self):
        return os.path.join(self.project.project_rel_path, 'versions',
                            self.slug.replace('_', '-'))
    
    @property
    def version_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.version_rel_path)
    
    def __str__(self):
        return self.name.replace('origin/', '')
        
    def save(self, *args, **kwargs):
        clean_name =  re.sub('\W+','-',self.name)
        self.slug = slugify(clean_name)
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['slug', 'project']

class Template(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(verbose_name="Slug")
    description = models.CharField(max_length=200, blank=True)
    template = models.FileField()
    version = models.ForeignKey(Version, on_delete=models.CASCADE, 
                                related_name = 'templates')
    
    @property
    def template_rel_path(self):
        return os.path.join(self.version.version_rel_path, 'templates',
                            self.slug)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        clean_name =  re.sub('\W+','-',self.name)
        self.slug = slugify(clean_name)
        super().save(*args, **kwargs)
        
    
class VarFile(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)
    varfile = models.FileField()
    template = models.ForeignKey(Template, on_delete=models.CASCADE,
                                 related_name = 'varfiles')
                                 
    def __str__(self):
        return self.name
        
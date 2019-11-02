import os
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.conf import settings
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
    def project_path(self):
        return os.path.join(settings.MEDIA_ROOT, 'projects', 
                            self.slug.replace('_', '-'))
    
    @property
    def working_dir(self):
        return os.path.join(self.project_path, 'checkout')
        
    def update_project(self):
        repo = Repo(
            name = self.name,
            url =  self.url,
            working_dir = self.working_dir )
        repo.update()
        # get revisions
        versions = repo.branches + repo.tags
        # update or create new versions
        for version in versions:
            Version.objects.update_or_create(
                name = version, 
                project = self,
                defaults = {
                    'hexsha': repo.hexsha(version),
                    'committed_date': repo.committed_date(version)
                }
            )
        # sort revisions by age
        # keep X most recent
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if not self.webhook_key:
            self.webhook_key = get_random_string(length=25)
        super().save(*args, **kwargs)
        self.update_project()
    
class Version(models.Model):
    name = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                related_name = 'versions')
    hexsha = models.CharField(max_length=200, unique=True)
    committed_date = models.DateTimeField()
    templates_dir = models.CharField(max_length=200, blank=True)
    vars_dir = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return self.name

class Template(models.Model):
    name = models.CharField(max_length=200)
    path = models.FileField(upload_to=None)
    version = models.ForeignKey(Version, on_delete=models.CASCADE, 
                                related_name = 'templates')
    
    def __str__(self):
        return self.name
    
class VarFile(models.Model):
    name = models.CharField(max_length=200)
    path = models.FileField(upload_to=None)
    template = models.ForeignKey(Template, on_delete=models.CASCADE,
                                 related_name = 'varfiles')
    
    def __str__(self):
        return self.name
        
# Utility


    
def update_version(version):
    pass
    
def delete_version(project):
    pass

def update_version(version):
    pass
    # load template def
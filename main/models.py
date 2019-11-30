import os, re, shutil, logging, json
from datetime import datetime, timezone
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse
from django.core.files import File
from main.build import Repo

log = logging.getLogger(__name__)

class Project(models.Model):
    PROVIDER_CHOICES = [
        ('GITEA', 'Gitea'),
        ('GITHUB', 'GitHub'),
    ]
    
    name = models.CharField(verbose_name="Project Name", max_length=200,
                            unique=True)
    slug = models.SlugField(verbose_name="Slug", unique=True)
    url = models.URLField(verbose_name="Project URL")
    template_def = models.CharField(verbose_name="Jinja2 Definition File",
                                    max_length=200)
    webhook_key = models.CharField(verbose_name="Webhook Key", max_length=200)
    provider = models.CharField(verbose_name="Git VCS Provider",
                                choices=PROVIDER_CHOICES,
                                max_length=200)
    
    @property
    def webhook_url(self):
        if self.slug:
            return reverse('webhook', kwargs={'project_slug': self.slug})
    
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
    def url(self):
        return self.project.url + '/commit/' + self.hexsha
    
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


"""
Utility Functions
"""
def load_template_def(path, filename, version_name):
    template_def_path = os.path.join(path, filename)
    try:
        with open(template_def_path) as f:
            return json.load(f)
    except OSError:
        log.info("failed to load template def: %s from version %s", filename, version_name)

        
def project_update_versions(instance):
    repo = Repo(
        name = instance.name,
        url =  instance.url,
        working_dir = instance.working_dir 
        )
    repo.update()
    # get revisions
    versions = repo.branches + repo.tags
    # update or create new versions
    for version in versions:
        committed_date = datetime.fromtimestamp(repo.committed_date(version), timezone.utc)
        hexsha = repo.hexsha(version)
        Version.objects.update_or_create(
            name = version, 
            project = instance,
            defaults = {
                'hexsha': hexsha,
                'committed_date': committed_date
            }
        ) 

def version_update_templates(instance):
    # checkout version
    version = instance
    repo = Repo(
            name = instance.project.name,
            url =  instance.project.url,
            working_dir = instance.project.working_dir 
            )
    repo.checkout_version(version=instance.name)
    # delete exist version templates from database
    instance.templates.all().delete()
    # cleanup version directory and copy new files
    if os.path.exists(instance.version_path):
        shutil.rmtree(instance.version_path)
    shutil.copytree(repo.working_dir, instance.version_path)
    # parse template_def, create templates => need try except here
    template_def = instance.project.template_def
    tmpl_json = load_template_def(repo.working_dir, template_def, instance.name)
    if tmpl_json:
        templates_dir = tmpl_json.get('templates_dir', '').strip("/")
        vars_dir = tmpl_json.get('vars_dir', '').strip("/")
        templates = tmpl_json.get('templates')
        for tmpl in templates:
            tmpl_obj = Template.objects.create(
                name = tmpl.get('name'),
                description = tmpl.get('description', ''),
                version = version
                )
            tmpl_obj.template = os.path.join(instance.version_rel_path, templates_dir, tmpl.get('name'))
            tmpl_obj.save()
            var_files = tmpl.get('var_files')
            for var_file in var_files:
                varfile_obj = VarFile.objects.create(
                    name = var_file,
                    template = tmpl_obj
                    )
                varfile_obj.varfile = os.path.join(instance.version_rel_path, vars_dir, var_file)
                varfile_obj.save()
        

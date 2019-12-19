import os, re, shutil, fnmatch, logging, json
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
    def base_url(self):
        hacked_url = self.url.split('://')[1]
        hacked_url = re.sub('.git$', '', hacked_url)
        return 'https://%s' % hacked_url
    
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
        if self.project.provider == 'GITEA':
            return self.project.base_url + '/src/commit/' + self.hexsha
        if self.project.provider == 'GITHUB':
            return self.project.base_url + '/tree/' + self.hexsha
    
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
        ordering = ['-committed_date']


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
    except json.JSONDecodeError:
        log.info("failed to load template def: %s from version %s - Error Decoding JSON File", filename, version_name)
    except OSError:
        log.info("failed to load template def: %s from version %s", filename, version_name)

def include_patterns(*patterns):
    """Factory function that can be used with copytree() ignore parameter"""
    def _ignore_patterns(path, names):
        keep = set(name for pattern in patterns for name in fnmatch.filter(names, pattern))
        ignore = set(name for name in names if name not in keep and not os.path.isdir(os.path.join(path, name)))
        return ignore
    return _ignore_patterns

        
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
    cur_versions = instance.versions.all()
    new_version_names = repo.branches + repo.tags
    # update or delete current versions
    for version in cur_versions:
        # update exist versions that have changed
        if version.name in new_version_names:
            if version.hexsha != repo.hexsha(version.name):
                log.info("updating version %s:%s %s->%s", instance.slug, version, version.hexsha, repo.hexsha(version.name))
                version.templates.all().delete()
                version.hexsha = repo.hexsha(version.name)
                version.committed_date = datetime.fromtimestamp(repo.committed_date(version.name), timezone.utc)
                version.save()
        # delete old versions
        else:
            log.info("deleting version %s:%s", instance.slug, version)
            version.delete()
    # create new versions
    for name in new_version_names:
        if name not in cur_versions.values_list('name', flat=True):
            log.info("creating version %s:%s", instance.slug, name)
            version = Version.objects.create(
                name = name,
                project = instance,
                hexsha = repo.hexsha(name),
                committed_date = datetime.fromtimestamp(repo.committed_date(name), timezone.utc)
            )
            version.save()
        
def version_create_template(instance, name, description):
    tmpl_abs_path = os.path.join(instance.version_path, 'templates', name)
    if os.path.exists(tmpl_abs_path):
        tmpl_obj = Template.objects.create(
            name = name,
            description = description,
            version = instance
            )
        tmpl_obj.template = os.path.join(instance.version_rel_path, 'templates', name)
        tmpl_obj.save()
        return tmpl_obj
    log.info("No template %s found for %s:%s", name, instance.project, instance)

def template_create_varfile(instance, name):
    varfile_abs_path = os.path.join(instance.version.version_path, 'vars', name)
    if os.path.exists(varfile_abs_path):
        varfile_obj = VarFile.objects.create(
            name = name,
            template = instance
        )
        varfile_obj.varfile = os.path.join(instance.version.version_rel_path, 'vars', name)
        varfile_obj.save()
        return varfile_obj
    log.info("No varfile %s found for %s:%s", name, instance.version.project, instance.version)

def version_update_templates(instance):
    """
    update a version
    """
    log.info("updating version %s:%s", instance.project.slug, instance)
    working_dir = instance.project.working_dir
    version_dir = instance.version_path
    template_def = instance.project.template_def
    # checkout version
    repo = Repo(
            name = instance.project.name,
            url =  instance.project.url,
            working_dir = working_dir 
            )
    repo.checkout_version(version=instance.name)
    # delete exist version templates from database
    instance.templates.all().delete()
    # cleanup version directory and copy new files
    if os.path.exists(instance.version_path):
        shutil.rmtree(instance.version_path)
    #shutil.copytree(repo.working_dir, instance.version_path)
    # parse template_def, create templates => need try except here
    tmpl_json = load_template_def(repo.working_dir, template_def, instance.name)
    if tmpl_json:
        # copy template files
        templates_dir = tmpl_json.get('templates_dir', '').strip("/")
        templates_src = os.path.join(working_dir, templates_dir)
        templates_dst = os.path.join(version_dir, 'templates')
        if os.path.isdir(templates_src):
            shutil.copytree(templates_src, templates_dst, ignore=include_patterns('*.j2','*.jinja2'))
        # copy var files
        vars_dir = tmpl_json.get('vars_dir', '').strip("/")
        vars_src = os.path.join(working_dir, vars_dir)
        vars_dst = os.path.join(version_dir, 'vars')
        if os.path.isdir(vars_src):
            shutil.copytree(vars_src, vars_dst, ignore=include_patterns('*.yml','*.yaml','*.json'))
        # index templates
        templates = tmpl_json.get('templates')
        for tmpl in templates:
            name = tmpl.get('name')
            description = tmpl.get('description', '')
            tmpl_obj = version_create_template(instance, name, description)
            if tmpl_obj:
                var_files = tmpl.get('var_files')
                for name in var_files:
                    template_create_varfile(tmpl_obj, name)
        

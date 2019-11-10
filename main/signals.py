import os, shutil, logging, json
from datetime import datetime, timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from main.models import Project, Version, Template, VarFile
from main.build import Repo

log = logging.getLogger(__name__)

"""
cleanup project directory after delete
"""
@receiver(post_delete, sender=Project)
def clean_project(sender, instance, **kwargs):
    shutil.rmtree(instance.project_path)

"""
clone/fetch project repo, create versions
"""
@receiver(post_save, sender=Project)    
def update_project(sender, instance, created, **kwargs):
    if created:
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

"""
parse version template def, create templates
"""
@receiver(post_save, sender=Version)
def update_templates(sender, instance, created, **kwargs):
    # checkout version
    repo = Repo(
            name = instance.project.name,
            url =  instance.project.url,
            working_dir = instance.project.working_dir 
            )
    repo.checkout_version(instance.name)
    # cleanup version directory and copy new files
    if os.path.exists(instance.version_path):
        shutil.rmtree(instance.version_path)
    shutil.copytree(repo.working_dir, instance.version_path)
    # parse template_def, create templates => need try except here
    template_def = instance.project.template_def
    try:
        with open(os.path.join(repo.working_dir, template_def)) as f:
            tmpl_json = json.load(f)
            templates_dir = tmpl_json.get('templates_dir', '')
            vars_dir = tmpl_json.get('vars_dir', '')
            templates = tmpl_json.get('templates')
            for tmpl in templates:
                tmpl_obj = Template.objects.create(
                    name = tmpl.get('name'),
                    description = tmpl.get('description', ''),
                    path = os.path.join(instance.version_path, templates_dir),
                    version = instance
                    )
                var_files = tmpl.get('var_files')
                for var_file in var_files:
                    VarFile.objects.create(
                        name = var_file,
                        path = os.path.join(instance.version_path, vars_dir),
                        template = tmpl_obj
                        )
    except Exception as e:
        log.exception("Failed to load template def: %s", template_def)

 
        
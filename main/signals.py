import os, shutil, logging, json
from django.core.files import File
from datetime import datetime, timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from main.models import Project, Version, Template, VarFile, project_update_versions, version_update_templates
from main.build import Repo

log = logging.getLogger(__name__)

"""
cleanup project directory after delete
"""
@receiver(post_delete, sender=Project)
def clean_project(sender, instance, **kwargs):
    if os.path.isdir(instance.project_path):
        shutil.rmtree(instance.project_path)

"""
clone/fetch project repo, create versions
"""
@receiver(post_save, sender=Project)    
def project_update_build_signal(sender, instance, created, **kwargs):
    if created:
        project_update_versions(instance)

"""
parse version template def, create templates
"""
@receiver(post_save, sender=Version)
def version_update_templates_signal(sender, instance, created, **kwargs):
    version_update_templates(instance)
    
"""
cleanup version directory after delete
"""
@receiver(post_delete, sender=Version)
def clean_version(sender, instance, **kwargs):
    if os.path.isdir(instance.version_path):
        shutil.rmtree(instance.version_path)

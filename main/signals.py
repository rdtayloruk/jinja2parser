import shutil
from datetime import datetime, timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from main.models import Project, Version
from main.build import Repo

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
            working_dir = instance.working_dir )
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
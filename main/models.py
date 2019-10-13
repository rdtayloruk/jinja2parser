from django.db import models

class Repo(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
#   templates = models.CharField(max_length=200)
    webhook_key = models.CharField(max_length=50)
    
class RepoVersion(models.Model):
    tag = models.ForeignKey(Repo, on_delete=models.CASCADE)
    #working_dir =  

class Template(models.Model):
    name = models.CharField(max_length=200)
    path = models.FileField(upload_to=None)
    repo_version = models.ForeignKey(Repo, on_delete=models.CASCADE)
    
class TemplateVars(models.Model):
    name = models.CharField(max_length=200)
    path = models.FileField(upload_to=None)
    parent_template = models.ForeignKey(Template, on_delete=models.CASCADE)
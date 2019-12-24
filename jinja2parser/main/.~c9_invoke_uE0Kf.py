from django.db import models

class Repo(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
#   templates = models.CharField(max_length=200)
    webhook_token = 
    
class RepoVersion(models.Model):
    tag = models.ForeignKey(Repo, on_delete=models.CASCADE)
    #working_dir =  

class Template(models.Model):
    pass

class TemplateVars(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
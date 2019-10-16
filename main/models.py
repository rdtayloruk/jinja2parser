from django.db import models

class Repo(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    template_def = models.CharField(max_length=200)
    webhook_key = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
class RepoVersion(models.Model):
    name = models.CharField(max_length=200)
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Template(models.Model):
    name = models.CharField(max_length=200)
    path = models.FileField(upload_to=None)
    repo_version = models.ForeignKey(Repo, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
class TemplateVars(models.Model):
    name = models.CharField(max_length=200)
    path = models.FileField(upload_to=None)
    parent_template = models.ForeignKey(Template, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
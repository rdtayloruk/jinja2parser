from django.contrib import admin
from django.contrib.auth.models import User

from .models import Repo

class RepoAdmin(admin.ModelAdmin):
    list_display = ("name","url")
    fields = ['name', 'url']
    readonly_fields = ['webhook_key']
    
    def webhook_key(self, instance):
        return User.objects.make_random_password(length=20)

admin.site.register(Repo)

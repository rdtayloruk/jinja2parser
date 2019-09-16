from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from jinja2 import Environment, meta, exceptions
import yaml
from main.gitea import GiteaAPI

GITEA_URL = "https://try.gitea.io/api/v1"
ORG = "rttest"

def index(request):
    context = {'repos': get_repos(ORG)}
    return render(request, 'main/index.html', context)

@require_POST
def convert(request):
    jinja2_env = Environment(trim_blocks=True, lstrip_blocks=True)

    # Load the template
    try:
        jinja2_tpl = jinja2_env.from_string(request.POST.get('template'))
    except (exceptions.TemplateSyntaxError, exceptions.TemplateError) as e:
        return HttpResponse("Syntax error in jinja2 template: {0}".format(e), status=400)

    # Load vars
    try:
        values = yaml.safe_load(request.POST.get('templateVars'))
    except (ValueError, yaml.YAMLError, TypeError) as e:
        return HttpResponse("Value error in YAML: {0}".format(e), status=400)
    
     # Render template
    try:
        rendered_jinja2_tpl = jinja2_tpl.render(values)
    except (exceptions.TemplateRuntimeError, ValueError, TypeError) as e:
        return HttpResponse("Error in your values input filed: {0}".format(e), status=400)

    return HttpResponse(rendered_jinja2_tpl)


def template_list(request):
    repo = request.GET.get('repo')
    templates = { 'templates': get_templates(ORG, repo) }
    return JsonResponse(templates)

def template(request):
    template = request.GET.get('template')
    pass


# Helpers

def get_repos(org):
    vcs =  GiteaAPI(GITEA_URL)
    repos = vcs.get_repos(org)
    repos = [r['name'] for r in repos]
    return repos

def get_templates(org, repo):
    vcs =  GiteaAPI(GITEA_URL)
    templates = vcs.get_contents_path(org, repo, "templates")
    print(templates)
    templates = [t['name'] for t in templates if t['name'].endswith('.j2')]
    return templates



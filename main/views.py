from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from jinja2 import Environment, meta, exceptions
import yaml, json, base64, re
from main.gitea import GiteaAPI

GITEA_URL = "https://try.gitea.io/api/v1"
ORG = "rttest"
TEMPLATE_PATH = "templates"
VARS_PATH = "vars"
TEMPLATE_DEF = "j2-templates.json"

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
    org = ORG
    path = TEMPLATE_DEF
    try:
        templates = json.loads(get_file(org, repo, path).decode('UTF-8'))
        print(templates)
        return JsonResponse(templates)
    except:
        return JsonResponse({"error": "not able to parse %s" % TEMPLATE_DEF})

def template(request):
    repo = request.GET.get('repo')
    path = request.GET.get('path') + "/" + request.GET.get('template')
    template = get_file(ORG, repo, path)
    return HttpResponse(template)



# Helpers

def get_repos(org):
    vcs =  GiteaAPI(GITEA_URL)
    repos = vcs.get_repos(org)
    repos = [r['name'] for r in repos]
    return repos

def get_templates(org, repo):
    vcs =  GiteaAPI(GITEA_URL)
    templates = vcs.get_contents_path(org, repo, TEMPLATE_PATH)
    print(templates)
    templates = [t['name'] for t in templates if t['name'].endswith('.j2')]
    return templates

def get_file(org, repo, path):
    vcs =  GiteaAPI(GITEA_URL)
    file_details = vcs.get_contents_path(org, repo, path)
    file_base64 = file_details.get('content')
    file_str = base64.b64decode(file_base64)
    return file_str

def get_manifest(org, repo):
    vcs =  GiteaAPI(GITEA_URL)
    path = TEMPLATE_DEF
    f = vcs.get_contents_path(org, repo, path)
    file_base64 = f.get('content')
    file_str = base64.b64decode(file_base64).decode('UTF-8')
    file_json = json.loads(file_str)
    print(file_json)
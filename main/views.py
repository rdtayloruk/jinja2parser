from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from jinja2 import Environment, meta, exceptions, DebugUndefined, StrictUndefined
import yaml, json, base64, re
from main.gitea import GiteaAPI

GITEA_URL = "https://try.gitea.io/api/v1"
ORG = "rttest"
TEMPLATE_PATH = "templates"
VARS_PATH = "vars"
TEMPLATE_DEF = "j2-templates.json"

vcs =  GiteaAPI(GITEA_URL)

def index(request):
    context = {'repos': get_repos(ORG)}
    return render(request, 'main/index.html', context)

@require_POST
def convert(request):
    payload = json.loads(request.body.decode('utf-8'))
    trim_blocks = payload.get('trim_blocks', True)
    lstrip_blocks = payload.get('lstrip_blocks', True)
    if payload.get('strict_undefined'):
        undefined = StrictUndefined
    else:
        undefined = DebugUndefined

    jinja2_env = Environment(trim_blocks=trim_blocks, lstrip_blocks=lstrip_blocks, undefined=undefined)

    # Load the template
    try:
        jinja2_tpl = jinja2_env.from_string(payload.get('template'))
    except (exceptions.TemplateSyntaxError, exceptions.TemplateError) as e:
        return HttpResponse("Syntax error in jinja2 template: {0}".format(e), status=400)

    # Load vars
    try:
        values = yaml.safe_load(payload.get('templateVars'))
    except (ValueError, yaml.YAMLError, TypeError) as e:
        return HttpResponse("Value Error in YAML: {0}".format(e), status=400)
    
     # Render template
    try:
        rendered_jinja2_tpl = jinja2_tpl.render(values)
    except (exceptions.TemplateRuntimeError, ValueError, TypeError) as e:
        return HttpResponse("Error in vars: {0}".format(e), status=400)

    return HttpResponse(rendered_jinja2_tpl)

def repo_template_list(request, owner, repo):
    try:
        templates = json.loads(get_file(owner, repo, TEMPLATE_DEF))
        print(templates)
        return JsonResponse(templates)
    except:
        return JsonResponse({"error": "not able to parse %s" % TEMPLATE_DEF})

def repo_file(request, owner, repo, path):
    path = path + "/" + request.GET.get('name')
    template = get_file(owner, repo, path)
    return HttpResponse(template)



# Helpers

def get_repos(org):
    repos = vcs.get_repos(org)
    repos = [r['full_name'] for r in repos]
    return repos

#def get_templates(org, repo):
#    templates = vcs.get_contents_path(org, repo, TEMPLATE_PATH)
#    print(templates)
#    templates = [t['name'] for t in templates if t['name'].endswith('.j2')]
#    return templates

def get_file(org, repo, path):
    file_details = vcs.get_contents_path(org, repo, path)
    file_base64 = file_details.get('content')
    file_str = base64.b64decode(file_base64).decode('UTF-8')
    return file_str
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from main.models import Project, Version, Template, VarFile
from jinja2 import Environment, meta, exceptions, Undefined, StrictUndefined
import yaml, json

def index(request):
    projects = Project.objects.all()
    context = {'projects': projects}
    return render(request, 'main/index.html', context)

@require_POST
def convert(request):
    print(request.POST.get('trim_blocks'))
    options = {}
    if request.POST.get('lstrip_blocks') == "true":
        options['lstrip_blocks'] = True
    elif request.POST.get('lstrip_blocks') == "false":
        options['lstrip_blocks'] = False
    if request.POST.get('trim_blocks') == "true":
        options['trim_blocks'] = True
    elif request.POST.get('trim_blocks') == "false":
        options['trim_blocks'] = False
    if request.POST.get('strict_undefined') == "true":
        options['undefined'] = StrictUndefined
    elif request.POST.get('strict_undefined') == "false":
        options['undefined'] = Undefined
        

    jinja2_env = Environment(**options)

    # Load the template
    try:
        jinja2_tpl = jinja2_env.from_string(request.POST.get('template'))
    except (exceptions.TemplateSyntaxError, exceptions.TemplateError) as e:
        return HttpResponse("Syntax error in jinja2 template: {0}".format(e), status=400)

    # Load vars
    try:
        values = yaml.safe_load(request.POST.get('templateVars'))
    except (ValueError, yaml.YAMLError, TypeError) as e:
        return HttpResponse("Value Error in YAML: {0}".format(e), status=400)
    
     # Render template
    try:
        rendered_jinja2_tpl = jinja2_tpl.render(values)
    except (exceptions.TemplateRuntimeError, ValueError, TypeError) as e:
        return HttpResponse("Error in vars: {0}".format(e), status=400)

    return HttpResponse(rendered_jinja2_tpl)
    
    
def project_versions(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    versions = project.versions.all()
    context = {'versions': versions }
    return render(request, 'main/version_dropdown_list.html', context)
    
def version_templates(request, version_id):
    version = get_object_or_404(Version, pk=version_id)
    templates = version.templates.all()
    context = {'templates': templates }
    return render(request, 'main/template_dropdown_list.html', context)

def template_varfiles(request, template_id):
    template = get_object_or_404(Template, pk=template_id)
    varfiles = template.varfiles.all()
    context = {'varfiles': varfiles }
    return render(request, 'main/varfile_dropdown_list.html', context)
    

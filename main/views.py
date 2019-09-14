from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from jinja2 import Environment, meta, exceptions
import yaml


def index(request):
    context = {'latest_question_list': ""}
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
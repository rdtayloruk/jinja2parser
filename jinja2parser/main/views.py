import hmac, logging, yaml, json
from hashlib import sha1, sha256

from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseServerError
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import force_bytes
from django.conf import settings
from main.models import Project, Version, Template, VarFile, project_update_versions
from jinja2 import Environment, meta, exceptions, Undefined, StrictUndefined, FileSystemLoader

log = logging.getLogger(__name__)

def index(request):
    projects = Project.objects.all()
    context = {'projects': projects}
    return render(request, 'main/index.html', context)



@require_POST
def convert(request):
    
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
    
    version_id = request.POST.get('version')
    version = Version.objects.get(pk=version_id) if version_id else None
        
    jinja2_env = None
    if version and request.POST.get('use_environment') == "true":
        jinja2_env = Environment(loader = FileSystemLoader(version.template_path), **options)
    else:
        jinja2_env = Environment(**options)

    # Load the template
    try:
        jinja2_tpl = jinja2_env.from_string(request.POST.get('template'))
    except (exceptions.TemplateSyntaxError, exceptions.TemplateError) as e:
        return HttpResponse("Template Syntax Error: {0}".format(e), status=400)

    # Load vars
    try:
        values = yaml.safe_load(request.POST.get('templateVars'))
    except (ValueError, yaml.YAMLError, TypeError) as e:
        return HttpResponse("YAML Error: {0}".format(e), status=400)
    
     # Render template
    try:
        rendered_jinja2_tpl = jinja2_tpl.render(values)
    except (exceptions.TemplateRuntimeError, ValueError, TypeError) as e:
        return HttpResponse("Template Render Error: {0}".format(e), status=400)

    return HttpResponse(rendered_jinja2_tpl)
    
    
def project_versions(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    versions = project.versions.all()
    context = {'versions': versions }
    return render(request, 'main/version_dropdown_list.html', context)
    
def version_templates(request, version_id):
    version = get_object_or_404(Version, pk=version_id)
    templates = version.templates.all()
    if not templates:
        return HttpResponse("No templates for {0} {1}".format(version.project, version), status=404)
    context = {'templates': templates }
    return render(request, 'main/template_dropdown_list.html', context)

def version_details(request, version_id):
    version = get_object_or_404(Version, pk=version_id)
    context = {'version': version }
    return render(request, 'main/version_details.html', context)

def template_varfiles(request, template_id):
    template = get_object_or_404(Template, pk=template_id)
    varfiles = template.varfiles.all()
    if not varfiles:
        return HttpResponse("No varfiles for {0} {1} {2}".format(template.version.project, template.version, template), status=404)
    context = {'varfiles': varfiles }
    return render(request, 'main/varfile_dropdown_list.html', context)

@csrf_exempt
@require_POST    
def webhook(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    
    if project.provider == "GITHUB":
        header_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
        if header_signature is None:
            return HttpResponseForbidden('Permission denied - Signature Missing')
    
        sha_name, signature = header_signature.split('=')
        if sha_name != 'sha1':
            return HttpResponseServerError('Operation not supported.', status=501)
    
        mac = hmac.new(force_bytes(project.webhook_key), msg=force_bytes(request.body), digestmod=sha1)
        if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
            return HttpResponseForbidden('Permission denied - Invalid Signature.')
            
        project_update_versions(project)
        
        return HttpResponse('success')
    
    if project.provider == "GITEA":
        header_signature = request.META.get('HTTP_X_GITEA_SIGNATURE')
        if header_signature is None:
            return HttpResponseForbidden('Permission denied - Signature Missing')
            
        payload = None
        if request.content_type == "application/json":
            payload = request.body
        else:
            payload = request.POST.get('payload')
            
        mac = hmac.new(force_bytes(project.webhook_key), msg=force_bytes(payload), digestmod=sha256)
        
        if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(header_signature)):
            return HttpResponseForbidden('Permission denied - Invalid Signature.')
        
        project_update_versions(project)
        
        return HttpResponse('success')
    

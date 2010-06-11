from coffin import shortcuts
from django.http import HttpResponse
from django.template import RequestContext

def get_title(html):
        p = re.compile('<title[^>]*>(.*?)</title>', re.IGNORECASE)
        m = p.search(html)
        if m:
            p = re.compile( '<[^>]*>')
            title = p.sub('', m.group(0))
            return title
        # set your own default
        return "Email from DevOps."


def render_to_string(template, context, request=None):
    if request:
        context_instance = RequestContext(request)
    else:
        context_instance = None
    return shortcuts.render_to_string(template, context, context_instance)


def render_to_response(template, context={}, request=None, mimetype="text/html"):
    response = render_to_string(template, context, request)
    return HttpResponse(response, mimetype=mimetype)


def render(template):
    """
    http://djangosnippets.org/snippets/821/

    Decorator for Django views that sends returned dict to render_to_response function
    with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

     - template: template name to use
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], request)
            elif isinstance(output, dict):
                return render_to_response(template, output, request)
            return output
        return wrapper
    return renderer

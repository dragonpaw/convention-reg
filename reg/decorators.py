#process a dict and remove by default the 'request' key
cleandict = lambda dlist, ignore = ['request'] : dict((key, val) for key, val in dlist.items() if key not in ignore)

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext

#render the template - assume a html format
def render_template(func):
    '''ensure the view using this has the template name matching it'''
    def render(*args, **kwargs):
        request = args[0]
        view_response = func(*args, **kwargs)
        if isinstance(view_response, HttpResponse):
            return view_response
        # Template name is "appname_viewname.html".
        template = func.__module__.split('.')[1] + "_" + func.__name__ + '.html'
        return render_to_response(
            template,
            cleandict(view_response),
            RequestContext(request)
        )
    return render

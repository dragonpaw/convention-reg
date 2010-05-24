from django.conf.urls.defaults import *
from convention import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^reg/', include('convention.reg.urls')),
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/reg/'} ),

    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name':'login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_DIR})
)

# Gotta put it somewhere, and not in settings.py.
from convention.lib.setup_log_handler import setup_handler
setup_handler()
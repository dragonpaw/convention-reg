#from django.conf import settings
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^reg/', include('reg.urls')),
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/reg/'} ),

    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name':'login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),
)

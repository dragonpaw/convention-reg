from django.conf.urls.defaults import *

urlpatterns = patterns('convention.reg.views',
    (r'^$', 'index'),
    (r'^member_add/$', 'member_add'),
    (r'^member_list/$', 'member_list'),
    (r'^member_view/(?P<id>\d+)/$', 'member_view'),
    (r'^membership_add/$', 'membership_add'),
    (r'^pending/$', 'print_pending'),
    (r'^pdf/$', 'print_pdf'),
    (r'^pdf/(?P<pages>\d+)/$', 'print_pdf'),

    (r'^report/members/all/$', 'report_member', ),
    (r'^report/members/public/$', 'report_member', {'public_only':True}),

    (r'^report/members/all/(?P<slug>[\w\-]+)/$', 'report_member'),
    (r'^report/members/public/(?P<slug>[\w\-]+)/$', 'report_member', {'public_only':True}),
)

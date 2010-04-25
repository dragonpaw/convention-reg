from django.conf.urls.defaults import *

urlpatterns = patterns('convention.reg.views',
    (r'^$', 'index'),

    (r'^person/add/$', 'person_add'),
    (r'^people/$', 'people_list'),
    (r'^person/(?P<id>\d+)/$', 'person_view'),

    (r'^cart/add/(?P<person_id>\d+)/(?P<type_id>\d+)/(?P<qty>\d+)/$', 'cart_add'),
    (r'^cart/add/(?P<person_id>\d+)/(?P<type_id>\d+)/$', 'cart_add', {'qty': 1}),
    (r'^cart/remove/(?P<person_id>\d+)/(?P<type_id>\d+)/$', 'cart_remove'),
    (r'^cart/checkout/$', 'checkout'),

    (r'^pending/$', 'print_pending'),
    (r'^pdf/$', 'print_pdf'),
    (r'^pdf/(?P<pages>\d+)/$', 'print_pdf'),

    (r'^report/members/all/$', 'report_member', ),
    (r'^report/members/public/$', 'report_member', {'public_only':True}),

    (r'^report/members/all/(?P<slug>[\w\-]+)/$', 'report_member'),
    (r'^report/members/public/(?P<slug>[\w\-]+)/$', 'report_member', {'public_only':True}),
)

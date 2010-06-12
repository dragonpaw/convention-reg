from coffin.conf.urls.defaults import *

urlpatterns = patterns('convention.reg.views',
    (r'^$', 'index'),

    (r'^person/add/$', 'person_add'),
    (r'^people/$', 'people_list'),
    (r'^person/(?P<id>\d+)/$', 'person_view'),

    (r'^cart/add/(?P<person_id>\d+)/(?P<type_id>\d+)/(?P<qty>\d+)/$', 'cart_add'),
    (r'^cart/add/(?P<person_id>\d+)/(?P<type_id>\d+)/$', 'cart_add', {'qty': 1}),
    (r'^cart/add/$', 'cart_add'),
    (r'^cart/remove/(?P<person_id>\d+)/(?P<type_id>\d+)/$', 'cart_remove'),
    (r'^cart/checkout/$', 'checkout'),

    (r'^selfserve/$', 'selfserve_index'),
    (r'^selfserve/check/email/$', 'selfserve_add_email'),
    (r'^selfserve/add/person/$', 'selfserve_add_person'),
    (r'^selfserve/add/membership/$', 'selfserve_add_membership'),
    (r'^selfserve/remove/(?P<email>.*?)/(?P<type_id>\d+)/$', 'selfserve_remove'),
    url(r'^selfserve/checkout/$', 'checkout', {'is_selfserve': True}, name='selfserve-checkout' ),

    (r'^pending/$', 'print_pending'),
    (r'^pdf/$', 'print_pdf'),
    (r'^pdf/(?P<pages>\d+)/$', 'print_pdf'),

    (r'^report/members/public/$', 'report_member', {'public_only':True}),

    (r'^report/members/all/(?P<slug>[\w\-]+)/$', 'report_member'),
    (r'^report/members/public/(?P<slug>[\w\-]+)/$', 'report_member', {'public_only':True}),

    (r'^report/members/approvals/(?P<slug>[\w\-]+)/$', 'approvals'),
)

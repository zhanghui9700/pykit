from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    (r'^v1/signup$', 'api.views.signup'),
    (r'^v1/status/(\d{5,})/$', 'api.views.status'),
    (r'^v1/termbind/$', 'api.views.termbind'),
    (r'^v1/unbind/$', 'api.views.unbind'),
    (r'^v1/bindstate', 'api.views.bindstate'),
    (r'^v1/addinfo/$', 'api.views.addinfo')
)

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    (r'^init$', 'openapi.views.init'),
    (r'^payment$', 'openapi.views.payment'),
)

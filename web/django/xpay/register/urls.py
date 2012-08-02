#-*- coding-utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib import databrowse
from django.conf import settings

urlpatterns = patterns('',
(r'^orders','register.views.orders'),
(r'^order/add','register.views.add_order'),
(r'^items','register.views.items'),
(r'^item/add','register.views.add_item'),
)

#!/bin/bash python
#-*- coding=utf-8 -*-

from django.conf.urls.defaults import patterns,url
from django.views.generic.simple import redirect_to

urlpatterns = patterns('',
    url(r'^$',redirect_to,{'url':'/manage/apply/list'}),
    url(r'^apply$','channel.views.apply_list'), 
    url(r'^apply/list$','channel.views.apply_list'),

    url(r'^apply/basic$','channel.views.apply_basic'),
    url(r'^apply/profile$','channel.views.apply_profile'),
    url(r'^apply/voucher$','channel.views.apply_voucher'),
    url(r'^apply/feerate$','channel.views.apply_feerate'),
)

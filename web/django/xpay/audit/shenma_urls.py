#-*- coding=utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.conf import settings

urlpatterns = patterns('',    
    (r'^$','audit.views_shenma.signup'),
    url(r'^signup$','audit.views_shenma.signup',name='shenma_basic_info'),
    url(r'^signup2$','audit.views_shenma.signup2',name='shenma_profile_info'),
    url(r'^signup3$','audit.views_shenma.signup3',name='shenma_upload_file'),
    url(r'^signup4$','audit.views_shenma.signup4',name='shenma_wait_audit'),
    url(r'^signup5$','audit.views_shenma.signup5',name='shenma_buy_terminal'),
    url(r'^signup6$','audit.views_shenma.signup6',name='shenma_buy_success'),

)

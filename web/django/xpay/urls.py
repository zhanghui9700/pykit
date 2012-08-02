#!/bin/bash python
#-*-coding=utf-8-*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib import databrowse
from django.conf import settings
from django.views.generic.simple import redirect_to

import audit.shenma_urls
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#shenma,目前神码渠道是最特殊的。
urlpatterns = patterns('', 
    url(r'^szsm/',include(audit.urls,namespace="foo",app_name="test")),
    url(r'^smsh$',redirect_to,{'url':'smsh/signup'}),
    url(r'^smsh/$','audit.views.signup'),
    url(r'^smqd/$','audit.views_shenma.signup'),
    url(r'^smqd/signup$','audit.views_shenma.signup',name='shenma_basic_info'),
    url(r'^smqd/signup2$','audit.views_shenma.signup2',name='shenma_profile_info'),
    url(r'^smqd/signup3$','audit.views_shenma.signup3',name='shenma_upload_file'),
    url(r'^smqd/signup4$','audit.views_shenma.signup4',name='shenma_wait_audit'),
    url(r'^smqd/signup5$','audit.views_shenma.signup5',name='shenma_buy_terminal'),
    url(r'^smqd/signup6$','audit.views_shenma.signup6',name='shenma_buy_success'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ADMIN_MEDIA_ROOT}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    (r'^data/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^api/',include('api.urls')),
    (r'^signin','audit.views.signin'),
    #(r'^databrowse/(.*)', databrowse.site.root),
   

    url(r'^(?P<group>[\w\W]*)/signup$','audit.views.signup'),
    url(r'^(?P<group>[\w\W]*)/signin$','audit.views.signin'),
    
    (r'^$','audit.views.signin'),
    url(r'^signup$','audit.views.signup',name='apply_basic_info'),
    url(r'^signup2$','audit.views.signup2',name='apply_profile_info'),
    url(r'^signup3$','audit.views.signup3',name='apply_upload_file'),
    url(r'^signup4$','audit.views.signup4',name='apply_wait_audit'),
    url(r'^signup5$','audit.views.signup5',name='apply_buy_terminal'),
    url(r'^signup6$','audit.views.signup6',name='apply_buy_success'),
    
    (r'^(?P<sid>\d{14})$','core.views.sign'),
    url(r'^account$','core.views.account',name='account_info'),
    (r'^tradelist','core.views.tradelist'),
    (r'^trade', 'core.views.tradedetail'),
    (r'^report$','core.views.report'),
    (r'^dlbill$','core.views.dlbill'),
   
    (r'^modifypwd$','core.views.modifypwd'),
    (r'^resetpwd$', 'core.views.resetpwd'),
    (r'^logout$', 'core.views.logout'),
    (r'^account$','core.views.account'),
    (r'^sendmobilecode$','audit.views.sendmobilecode'),
    (r'^blocked$','audit.views.blocked'),
    (r'^puzzled$','audit.views.puzzled'),
    (r'^agreement$', 'audit.views.agreement'),
    (r'^privacy$', 'audit.views.privacy'),
    (r'^charge_notify', 'audit.views.charge_notify'),
    (r'^charge_return', 'audit.views.charge_return'),
    (r'^validate$','audit.views.validate'),
    
    #(r'^stat$','mis.stat.stat'),
 
    (r'^upgrade/$','audit.upgradeview.upgrade_index'),
    (r'^upgrade/upload/$','audit.upgradeview.upgrade_upload'),
    (r'^upgrade/upload/image/$','audit.upgradeview.upgrade_save_image'),
    (r'^upgrade/waitaudit/$','audit.upgradeview.upgrade_waitaudit'),
    (r'^preview/(?P<uid>\d{5,})/(?P<scale>(small|middle|large|original))/(?P<name>\w*(.jpg|.jpeg|.png))', 'audit.upgradeview.voucher_preview'),
    (r'^upgrade/remove/image/$','audit.upgradeview.upgrade_remove_image'),
     
    #(r'^upbasic$','audit.upgradeview.uploadbasic'),
    #(r'^upgold$','audit.upgradeview.uploadgold'),
    #(r'^preview/(\w*)/(\d{0,})', 'audit.upgradeview.preview'),
    #(r'^upload/(\w*)/$', 'audit.upgradeview.upload_img'),
    
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^template/$','core.views.show_template',name='show_template'),
    )

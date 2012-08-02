from django.conf import settings
from django.conf.urls.defaults import patterns,url
from django.contrib.auth.decorators import login_required
from mis.views import typist_list,typist_input
from mis.audit_views import auto_result,manual_audit,voucher_confirm,manual_submit

#~/typist/xxxx
urlpatterns = patterns('mis.views',
   url(r'^list/$',login_required(typist_list),name='mis_typist_list'),
   url(r'^list/(?P<current>\d{5,})/$',login_required(typist_list),name='mis_typist_list_user'),
   url(r'^input/$',login_required(typist_input),name='mis_typist_input'),
)

#~/audit/xxxx
urlpatterns += patterns('mis.audit_views',
   url(r'^result/$',login_required(auto_result),name='audit_result'),
   url(r'^manual/(?P<upid>\d{1,})/$',login_required(manual_audit),name='manual_audit'),
   url(r'^manual/submit/$',login_required(manual_submit),name='manual_submit'),
   #url(r'^voucher/confirm/$',login_required(voucher_confirm),name='voucher_confirm'),
)

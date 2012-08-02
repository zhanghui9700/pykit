#coding=utf-8

from django.contrib import admin
from util.multidb_admin import CoreDBModelAdmin

from models import *

class AppInfoAdmin(admin.ModelAdmin):
    list_display = ('app_name','app_ver','app_minver','os','os_ver','update_type','domain','url','upload_retries')
    def save_model(self,request,obj,form,change):
        if form.is_valid():
            apl = form.save(commit=False)
            app_name = apl.app_name
        msg = u'管理员[%s]添加客户端[%s]'%(request.user.id,app_name)
        OpLog.objects.log_action(request.user.id,4,u'添加客户端',msg)
class FeedBackAdmin(admin.ModelAdmin):
    list_display = ('busicd','userid','terminalid','phonemodel','networkmode','feedbackmsg')
    search_fields = ('userid',)
    list_filter = ('phonemodel','networkmode')

class StatAdmin(admin.ModelAdmin):
    list_display = ('busicd','userid','terminalid','phonemodel','networkmodel','errormsg')
    search_fields = ('userid',)
    list_filter = ('phonemodel','networkmodel') 
class OpLogAdmin(CoreDBModelAdmin):
    list_display = ('id','admin_id','op_type','action','detail','memo','notify_type','action_time')
    search_fields = ['admin_id']
    list_filter = ('op_type',)

    def has_add_permission(self,request):
        return False

    def has_change_permission(self,request,obj=None):
        return False

    def change_view(self,request,object_id,extra_context=None):
        context = {
            'show_save':False,
            'show_save_as_new':False,
            'show_save_and_continue':False,
            'show_save_and_add_other':False,
        }
        context.update(extra_context or {})
        return super(type(self),self).change_view(request,object_id,context)
admin.site.register(Appinfo, AppInfoAdmin)
admin.site.register(FeedBack, FeedBackAdmin)
admin.site.register(Stat, StatAdmin)
#admin.site.register(OpLog,OpLogAdmin)


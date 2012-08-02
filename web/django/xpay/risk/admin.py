#coding=utf-8
import datetime
from django.contrib import admin
from django.contrib.auth.models import User
from django import forms

from risk.models import UserParam,Result,TradeRecord,LoginRecord,UserDay,CoreLevel,Risk,RiskCode

from util.multidb_admin import MultiDBModelAdmin
from util.common import export_as_xls
export_as_xls.short_description = u'选中项导出为Excel'


class UserParamAdmin(MultiDBModelAdmin):
    list_display = ('userid', 'type', 'city', 'latitude', 'longitude',
        'loginpwderr', 'adminpwderr', 'smalltranserr', 'display_allowedamount',
    )

class ResultAdmin(MultiDBModelAdmin):
    list_display = ('userid', 'syssn', 'busicd','trans_ckdate', 'display_ret','rstype','rstypeid')
    search_fields = ('userid','syssn',)
    list_filter = ('ckdate','ret')
    actions = [export_as_xls]
    def has_add_permission(self, request):
        return False

class TradeRecordForm(forms.ModelForm):
    class Meta:
        model=TradeRecord
        fields = ('id', 'busicd', 'userid','terminalid','psamid','appid','udid','syssn',\
        'riskret','respcd','cardcd','cardtp','sysdtm')

class TradeRecordAdmin(MultiDBModelAdmin):
    list_display = ('userid','display_respcd','display_riskret','busicd','display_txamt','syssn','trans_date','cardcd','cardtp')
    search_fields=('terminalid','cardcd','syssn','userid')
    list_filter = ('riskret','cardtp')
    form=TradeRecordForm 
    actions = [export_as_xls]

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

class LoginRecordAdmin(MultiDBModelAdmin):
    list_display = ('lid', 'userid','terminalid','psamid', 'appid','display_respcd','display_riskret','trans_sysdate')

table = 'userday_%s' %(datetime.datetime.now().strftime('%Y%m%d'))

class UserDayForm(forms.ModelForm):
    class Meta:
        model=UserDay
        
        
class UserDayAdmin(MultiDBModelAdmin):
    list_display = ('userid', 'display_tradeamount','tradecount','tradecyc','display_creditcardamount','creditcardcount','display_debitamount','debitcount','tradeexceedamocount','tradeexceedcount',\
                    'creditexceedamocount','creditexceedcount','creditescalehigh','allowedcount','dividecount','intcount','passerrcount','display_intamount','balancequerycount','display_notimeamount','display_noareaamount','loginpwderr')
    form=UserDayForm
    actions = [export_as_xls]
    def has_add_permission(self, request):
        return False
    def queryset(self, request):
        global table
        if request.GET.get('e') != None:
            table = 'userday_%s' %(request.GET.get('e'))
        UserDay._meta.db_table = table
        qs = super(UserDayAdmin, self).queryset(request)

        return qs

class CoreLevelAdmin(admin.ModelAdmin):
    list_display = ('level','display_dayamount','display_weekamount','display_monthamount','daycount','weekcount','monthcount','dayauthcount','weekauthcount','monthauthcount','display_daycardamount','display_weekcardamount','display_monthcardamount','daycardcount','weekcardcount','monthcardcount','maxamount','creditmaxamount','daybebitcount','weekbebitcount','monthbebitcount','daybebitamount','weekbebitamount','monthbebitamount',)
    #exclude = ('is_delete',)

class RiskAdmin(admin.ModelAdmin):
    list_display = ('id','tradetype','cardtype','currency','validdate','validtime','validtime','validarea','display_maxamount','display_creditmaxamount','maxpassworderr','smallamount','alarmcreditrate','alarmintrate','dividecount',)

class RiskCodeAdmin(admin.ModelAdmin):
    list_display = ('nid','code','name','parentnid','desc','remark1','remark2','remark3','is_delete')

admin.site.register(RiskCode,RiskCodeAdmin)
admin.site.register(Risk,RiskAdmin)
admin.site.register(CoreLevel,CoreLevelAdmin)
admin.site.register(LoginRecord, LoginRecordAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(UserParam, UserParamAdmin)
admin.site.register(TradeRecord, TradeRecordAdmin)
admin.site.register(UserDay, UserDayAdmin)

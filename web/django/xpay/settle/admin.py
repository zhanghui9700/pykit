#coding=utf-8
import pdb,datetime
import os
from django.contrib import admin
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.conf.urls.defaults import patterns, include, url
#from django.utils.translation import ugettext_lazy as _
#from django.contrib.admin import SimpleListFilter

from models import Debit,Settle,SettleTrade,SettleStatis,Adjust,Account,Period,Unequal,Earning
from util.multidb_admin import SettleDBModelAdmin
import qfpay

def format_debit(debit):
    fields = []
    fields.append('%s%010d' %(debit.expectdate.strftime('%Y%m%d'),debit.userid)) #打款日期
    fields.append('RMB') #人民币
    fields.append(debit.bankaccount) #银行账号
    fields.append(debit.name) #收款人
    fields.append(debit.bankname) #收款银行
    fields.append('%.2f' %(debit.payamt/100.0)) #打款金额
    return ','.join(fields)

def export_to_txt(post):
    try:
        date = post['date']
    except:
        return HttpResponse(u'Please input the date!!!')
    import cStringIO
    file = cStringIO.StringIO()
    debits = Debit.objects.filter(expectdate = datetime.datetime.strptime(date, '%Y%m%d')).order_by('userid')
    
    for debit in debits:
        rec = format_debit(debit)
        file.write(rec.encode('utf-8'))
        file.write('\n')
    response = HttpResponse(file.getvalue(), mimetype='application/text')
    response['Content-Disposition'] = 'attachment; filename=debit.csv'
    response['Content-Length'] = file.tell()
    file.close()
    return response

class DebitAdmin(SettleDBModelAdmin):
    list_display = ('userid','name','bankname','bankaccount','dis_payamt','expectdate','expectdate','status')
    search_fields = ['userid','name']
    list_filter = ('expectdate',)

    def changelist_view(self,request,extra_context=None):
        post = request.POST
        response = None

        try:
            date = post['download']
            response = export_to_txt(post)
        except:
            yesterday = datetime.datetime.now().date()-datetime.timedelta(days=1)
            extra_context = dict()
            extra_context['debit_date'] = yesterday.strftime('%Y%m%d')
            response = super(type(self),self).changelist_view(request,extra_context)
        return response
        
class SettleAdmin(SettleDBModelAdmin):
    list_display = ('userid','dis_curperiod','dis_curstart','dis_curend','dis_debit','settlecnt','dis_tradenum','dis_settlenum','dis_payfee','dis_qffee','dis_chnlfee','dis_adjust','dis_manual','dis_lastsettle','dis_lastdebit','xbill_date','pass_settle')
    search_fields = ('userid','pid__id')

    def get_urls(self):
        urls = super(SettleAdmin,self).get_urls()
        my_urls = patterns('',
            (r'dlbill/$', self.dlbill),
            (r'pass/$', self.passed_settle),
        )
        return my_urls+urls

    def passed_settle(self, request):
        try:
            date = request.GET['pid']
            userid = int(request.GET['userid'])
        except:
            return Http404
        print 'passed'
        return HttpResponseRedirect('/admin/settle/settle/')

    def dlbill(self, request):
        try:
            date = request.GET['date']
            userid = request.GET['userid']
        except:
            return Http404

        from django.core.servers.basehttp import FileWrapper
        import mimetypes

        filename = qfpay.BILLS_LOCATION+`int(userid)`+'/'+date+'.xls'
        try:
            wrapper = FileWrapper(open(filename))
            content_type = mimetypes.guess_type(filename)[0]
        except:
            raise Http404
        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Length'] = os.path.getsize(filename)
        response['Content-Disposition'] = 'attachment; filename=%d_%s.xls' %(int(userid),date)
        return response

    def queryset(self,request):
        if request.POST.has_key('zero'):
            return super(SettleAdmin,self).queryset(request).filter(settlecnt=0)
        elif request.POST.has_key('unzero'):
            return super(SettleAdmin,self).queryset(request).filter(settlecnt__gt=0)
        else:
            return super(SettleAdmin,self).queryset(request)

#执行结算
def run_settle(date, request):

    fn = '%s%s.txt' %(qfpay.SETTLE_DIR, date)
    file = open(fn, 'w')
    file.write(str(request.user.id)+'\n')
    file.write(date)
    file.close()

class SettleTradeAdmin(SettleDBModelAdmin):
    list_display = ('userid','groupid','syssn','settletype','stldate','tradetype','merchantid','cardtp','cardcd','dis_tradenum','dis_settlenum','dis_payfee','dis_qffee','dis_chnlfee')
    list_filter = ('merchantid','stldate')
    search_fields = ['userid']
    
    def changelist_view(self,request,extra_context=None):
        extra_context = extra_context or {}
        now = datetime.datetime.now()
        date_argv = []
        try:
            date = request.GET['e']
        except:
            date = now.date().strftime('%Y%m%d')
        for i in range(-14,1):
            date_argv.append(now + datetime.timedelta(days=i))
        extra_context['date_argv'] = date_argv
        extra_context['stldate'] = (datetime.datetime.today()-datetime.timedelta(days=1)).strftime('%Y%m%d')
        return super(type(self),self).changelist_view(request,extra_context)

    def get_changelist(self, request, **kwargs):
        cl = super(SettleTradeAdmin,self).get_changelist(request,**kwargs)
        try:
            date=request.GET['e']
            setattr(cl,'table',date)
        except:
            pass
        return cl

    def queryset(self, request):
        qs = super(SettleTradeAdmin,self).queryset(request)
        #Execute the settle process
        try:
            is_exe_settle = request.POST['settle']
            date = request.POST['stldate']
            run_settle(date, request)
        except:
            if request.GET.get('e') != None:
                self.table = 'settle_%s' %(request.GET.get('e'))
            else:
                try:
                    self.table = self.table 
                except:
                    self.table = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y%m%d')
            self.model._meta.db_table = self.table
        return qs

#class ZeroTradeFilter(SimpleListFilter):
#    title = _(u'无交易')
#    parameter = 'tradecnt'
#
#    def lookups(self, request, model_admin):
#        
#        return (
#            (u'zero', _(u'无交易')),
#            (u'unzero', _(u'有交易')),
#            )
#    def queryset(self, request, queryset):
#        if self.value() == 'zero':
#            return queryset.filter(tradecnt=0)
#        if self.value() == 'unzerio':
#            return queryset.filter(tradecnt!=0)
#
class SettleStatisAdmin(SettleDBModelAdmin):
    list_display = ('groupid', 'stldate', 'usercnt','tradecnt', 'dis_tradenum','dis_settlenum','dis_payfee','dis_qffee','dis_chnlfee')
    #list_filter = (ZeroTradeFilter,)

class AdjustAdmin(SettleDBModelAdmin):
    
    list_display = ('userid','adjust_type','dis_adjustnum','adjust_date','adjust_state')

class AccountAdmin(SettleDBModelAdmin):
    list_display = ('userid', 'srcid', 'feeratio', 'creditratio', 'maxfee','creditmaxfee','dis_interval','dis_income','settlecount','dis_settlenum','dis_remaining')
    search_fields = ['userid']

class PeriodAdmin(SettleDBModelAdmin):
    list_display = ('id', 'lastid','start','end')

#调为平帐
def make_equal(modeladmin, request, queryset):
    try:
        stldate = request.POST['expect']
        datetime.datetime.strptime(stldate, '%Y%m%d')
    except:
        return HttpResponse(u'请输入调账日期!')

    SettleTrade._meta.db_table = 'settle_%s' %stldate
    for unequal in queryset:
        equal = SettleTrade.objects.get_or_create(userid=unequal.userid,
        chnlid=unequal.paychnl,merchantid=unequal.merchantid,termid=unequal.terminalid,
        stldate=unequal.stldate,syssn=unequal.syssn,mcc=unequal.mcc,tradetype=unequal.tradetype,
        currency=unequal.currency,tradedtm=unequal.tradedtm,cardtp=unequal.cardtp,
        cardcd=unequal.cardcd,issuerbank=unequal.issuerbank,origsyssn=unequal.refid,
        tradenum=unequal.tradenum,payfee=unequal.tradefee)
        unequal.state, unequal.auditor =1,request.user.id
        unequal.save()

    return HttpResponse(u'调账完成!')

make_equal.short_description = u'调为平帐'

class UnequalAdmin(SettleDBModelAdmin):
    
    list_display = ('userid', 'tradetype', 'errcode','srcpid', 'merchantid','cardcd','state',
        'cardtp','issuerbank','tradedtm','terminalid','syssn','refid','display_tradenum')
    search_fields = ['userid', 'syssn']
    list_filter = ['srcpid','state', 'merchantid','tradetype']
    readonly_fields = ['userid','errcode','paychnl','merchantid','tradetype',
    'refid','origdtm','mcc','issuerbank','currency','cardcd','cardtp','tradenum',
    'tradedtm','tradefee','stldate','syssn','terminalid','srcpid','dstpid','auditdate','auditor','chnlrtn']
    actions = [make_equal]
    
class EarningAdmin(SettleDBModelAdmin):
    list_display = ('dis_pid', 'dis_should', 'dis_realpay', 'dis_payed','dis_unpayed','dis_earning','dis_unequal')

admin.site.register(Debit,DebitAdmin)
admin.site.register(Settle,SettleAdmin)
admin.site.register(SettleTrade, SettleTradeAdmin)
admin.site.register(SettleStatis, SettleStatisAdmin)
admin.site.register(Adjust, AdjustAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Unequal, UnequalAdmin)
admin.site.register(Earning, EarningAdmin)

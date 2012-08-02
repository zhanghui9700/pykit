#!/usr/bin/env python
#coding=utf-8
import sys,datetime,pdb
import time, json
from django.contrib.auth.models import User
from django.contrib import admin,databrowse
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from core.models import Person,SPerson,Merchant,UserProxy
from models import Record,Channel
from util.define import UserType
from util.common import export_as_xls
export_as_xls.short_description = u'选中项导出为Excel'

class RecordAdmin(admin.ModelAdmin):
    list_display = ('pk_link','trade_sign_link','userid_link','display_usermobile','display_username','busicd','cardtp','cardcd','issuerbank','display_txamt','clisn','syssn','origssn','authid','retcd','status','cancel','sign','display_contact','display_contact_mail','display_contact_sms','terminalid','chnlid')
    
    list_display_link = ('userid_link','syssn')
    list_filter = ('status','sign','busicd','cancel','chnlid')
    search_fields = ('syssn','cardcd','userid')
    
    actions=[export_as_xls]
    
    change_form_template = 'admin/trade/change_form.html'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self,request,obj=None):
        return False

    def change_view(self,request,object_id,extra_context=None): 
        self.readonly_fields = self.get_all_fields()
        extra_context = extra_context or {}
        extra_context['readonly'] = True
        try:
            self.model._meta.db_table = self.table
            return super(type(self),self).change_view(request,object_id,extra_context)
        except:
            return HttpResponseRedirect('/admin/%s/%s/' % (self.model._meta.app_label,self.model.__name__.lower()))            
   
    def changelist_view(self,request,extra_context=None):
        extra_context = extra_context or {}
        now = datetime.datetime.now()
        date_argv = []
        for i in range(-14,1):
            date_argv.append(now + datetime.timedelta(days=i))
        extra_context['date_argv'] = date_argv
        return super(type(self),self).changelist_view(request,extra_context)

    def trade_sign_link(self,obj):
        try:
            return '<a target="_blank" href="https://qfpay.com/{0}?cardno={1}">{0}</a>'.format(obj.syssn,obj.cardcd[-6:])
        except:
            return os.syssn
    trade_sign_link.short_description = u'签名小票'
    trade_sign_link.admin_order_field = 'syssn'
    trade_sign_link.allow_tags = True

    def pk_link(self,obj):
        d = obj.sysdtm or datetime.datetime.now()
        s =  u'<a href="/admin/%s/%s/%s/?e=%s">%s</a>' % (self.model._meta.app_label,self.model.__name__.lower(),obj.id,d.strftime('%Y%m%d'),d.strftime('%Y-%m-%d %H:%M:%S'))
        return s
    pk_link.short_description = u'交易时间'
    pk_link.allow_tags = True
    pk_link.admin_order_field=u'sysdtm'

    def userid_link(self,obj):
        try:
            u = UserProxy.objects.get(id=obj.userid)
            core = u.get_xuser()
            if u.user_type == UserType.PERSON:
                return u'<a href="/admin/%s/%s/%s">%s</a>' % (Person._meta.app_label,Person.__name__.lower(),u.get_xuser().id,obj.userid)
            elif u.user_type == UserType.SPERSON:
                return u'<a href="/admin/%s/%s/%s">%s</a>' % (SPerson._meta.app_label,SPerson.__name__.lower(),u.get_xuser().id,obj.userid)
            elif u.user_type == UserType.MERCHANT:
                return u'<a href="/admin/%s/%s/%s">%s</a>' % (Merchant._meta.app_label,Merchant.__name__.lower(),u.get_xuser().id,obj.userid)
            else:
                return obj.userid
        except Exception,e:
            return obj.userid
    userid_link.short_description = u'商户编号'
    userid_link.allow_tags = True
    userid_link.admin_order_field=u'userid'

    def get_all_fields(self):
        l = []
        for field in self.model._meta.fields:
            l.append(field.name)

        return tuple(l)

    def queryset(self,request):
        if request.GET.get('e') != None:
            self.table = 'record_%s' %(request.GET.get('e'))
        else:
            try:
                self.table = self.table 
            except:
                self.table = u'record_%s' % datetime.datetime.now().strftime('%Y%m%d')
        self.model._meta.db_table = self.table
        return super(RecordAdmin, self).queryset(request)

    def mapview(self,request,extra_context=None):
        def myquery(sql):
            from django.db import connection, transaction, connections
            cursor = connections["trade"].cursor()
            cursor.execute(sql)
            desc = cursor.description
            return [dict(zip([col[0] for col in desc],row)) for row in cursor.fetchall()]

        def txamt_format(x):
            a = str(x/100)
            pa = a.split('.')
            p1 = range(len(pa[0]), 0, -3)
            p1.append(0)
            p1.reverse()
            r1 = [pa[0][p1[i]: p1[i+1]] for i in range(0,len(p1)-1)]
            if len(pa) == 2:
                return ','.join(r1) + '.' + pa[1]
            return ','.join(r1)
           
        sql = "select id,userid,busicd,txamt,sysdtm,longitude,latitude from record_%d%02d%02d where (busicd='000000' or busicd='201000') and status=1 and cancel=0 and txamt>1000 order by id" % time.localtime()[:3]
        #print sql
        
        busicd_map = {'000000':u'消费', '201000': u'消费撤销'}
        qs = Record.objects.raw(sql) 
        #qs = myquery(sql)
        txamt = 0
        qslen = 0
        '''
        for row in qs:
            txamt += row["txamt"] 
            row['sysdtm'] = str(row['sysdtm'])
            row['msg'] = u'%d 于 %s 收到%s %s 元' % (row['userid'], 
                row['sysdtm'], busicd_map[row['busicd']], txamt_format(row['txamt']))
            qslen += 1
        '''
        rows = []
        for row in qs:
            if row.busicd == '000000':
                txamt += row.txamt
            elif row.busicd == '201000':
                txamt -= row.txamt
            row.sysdtm = str(row.sysdtm)
            row.msg = u'%s 于 %s 收到%s %s 元' % (row.display_username(), 
                row.sysdtm, busicd_map[row.busicd], row.display_txamt())
            qslen += 1
            rows.append({'txamt':txamt_format(row.txamt), 
                         'busicd':busicd_map[row.busicd],
                         'sysdtm': str(row.sysdtm),
                         'longitude': row.longitude,
                         'latitude': row.latitude,
                         #'display_username': row.display_username(),
                         'msg':row.msg})


        if not request.GET.get('m'):
            return render_to_response('admin/trade/mapview.html', {},
                #{'txamt':0, 'txamt_str':txamt_format(txamt), 
                #'txitem':qslen, 'record':qs},
                context_instance=RequestContext(request)) 
        else:
            #dumper = DataDumper()
            #dumper.selectObjectFields('Record',['userid','display_username','busicd','display_txamt', 'longitude', 'latitude', 'sysdtm'])
            x = json.dumps({'record':rows, 'txamt':'%.2f'%(txamt/100.0), 'txitem':qslen})
            return HttpResponse(x)
        

    def get_urls(self):
        from django.conf.urls.defaults import patterns,url
        custom_urls = patterns('',
            url(r'^mapview',self.mapview,name='mapview'),
        )
        return custom_urls + super(type(self),self).get_urls() 

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name','zmk','zpk','mcc','chcd','inscd', 'code', 'regioncd','mchntid')

admin.site.register(Channel,ChannelAdmin)
admin.site.register(Record,RecordAdmin)

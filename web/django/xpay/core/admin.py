#!/usr/bin/env python
#coding=utf-8

import datetime,pdb
import json

from django.contrib.auth.models import User
from django.http import HttpResponse,HttpResponseRedirect
from django.conf.urls.defaults import patterns,url
from django import forms
from django.contrib import admin
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.forms.formsets import all_valid
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.contrib.admin import helpers
from django.contrib.admin.util import unquote
from django.db import models
from mis.models import Terminal,Psam
from models import Person,SPerson,Merchant,TerminalBind,ChannelUser,Recharge,Invoice,Profile
from util.define import TerminalUsedState,TerminalState
from util.common import export_as_xls
export_as_xls.short_description = u'选中项导出为Excel'
from audit.admin import MisDBModelAdmin
from settle.models import Account

class BaseForm(forms.ModelForm):
    allowed_amountv1 = forms.IntegerField(label=u'借记卡可允许上限',required=False,initial=50,help_text=u'以百为输入单位，范围：1-32767，例如：5000元，输入50')
    allowed_amountv2 = forms.IntegerField(label=u'信用卡可允许上限',required=False,initial=50,help_text=u'以百为输入单位，范围：1-32767，例如：5000元，输入50')
    creditratio = forms.FloatField(label=u'信用卡费率',required=False)
    feeratio = forms.FloatField(label=u'储值卡费率',required=False)
    maxfee = forms.IntegerField(label=u'封顶',required=False)
    userlevel = forms.IntegerField(label=u'商户等级',required=False)

    def clean_allowed_amountv1(self):
        allowed_amountv1 = self.data.get('allowed_amountv1')
        if len(allowed_amountv1)==0:
            raise forms.ValidationError(u'输入不能为空')
        if int(allowed_amountv1)>32767:
            raise forms.ValidationError(u'超出范围')
        if int(allowed_amountv1)<1:
            raise forms.ValidationError(u'不能小于1')
        return int(allowed_amountv1)

    def clean_allowed_amountv2(self):
        allowed_amountv2 = self.data.get('allowed_amountv2')
        if len(allowed_amountv2)==0:
            raise forms.ValidationError(u'输入不能为空')
        if int(allowed_amountv2)>32767:
            raise forms.ValidationError(u'超出范围')
        if int(allowed_amountv2)<1:
            raise forms.ValidationError(u'不能小于1')
        return int(allowed_amountv2)

class PersonForm(BaseForm):
    class Meta:
        model = Person

class BaseAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, extra_context=None):
        "The 'change' admin view for this model."
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if request.method == 'POST' and "_saveasnew" in request.POST:
            return self.add_view(request, form_url='../add/')

        ModelForm = self.get_form(request, obj)
        formsets = []
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request, new_object),
                                       self.inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object, prefix=prefix,
                                  queryset=inline.queryset(request))

                formsets.append(formset)

            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                change_message = self.construct_change_message(request, form, formsets)
                self.log_change(request, new_object, change_message)
                return self.response_change(request, new_object)

        else:
            form = ModelForm(instance=obj)
            try:
                acc = Account.objects.filter(userid = obj.user.id)[0]
            except:
                acc = []
            allowed_amountv1=obj.allowed_amount>>16
            allowed_amountv2=obj.allowed_amount&65535
            form.__dict__.get('initial')['allowed_amountv1']=allowed_amountv1
            form.__dict__.get('initial')['allowed_amountv2']=allowed_amountv2
            form.__dict__.get('initial')['userlevel']=obj.user.user_level
            if acc:
                form.__dict__.get('initial')['feeratio']=acc.feeratio
                form.__dict__.get('initial')['creditratio']=acc.creditratio
                form.__dict__.get('initial')['maxfee']=acc.maxfee
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request, obj), self.inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=obj, prefix=prefix,
                                  queryset=inline.queryset(request))
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj),
            self.prepopulated_fields, self.get_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': "_popup" in request.REQUEST,
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, change=True, obj=obj)

class PersonAdmin(BaseAdmin):
    list_display = ('user','display_userid','username','nickname','display_user_level','city','id_number','bank_account','display_creditratio','display_feeratio','allowed_trade','allowed_time','allowed_card','allowed_currency','trans_last_modify')
    exclude = ('allowed_amount',)
    raw_id_fields = ('user',)
    search_fields = ['user__username','user__id','username']
    list_filter = ('city',)
    actions = [export_as_xls]
    form=PersonForm
    
    
    
    
    
    def save_model(self,request,obj,form,change):
        if request.method =='POST':
            form=PersonForm(request.POST)
            if form.is_valid():
                #pdb.set_trace()
                if not change:
                    Personc=form.cleaned_data
                    allowed_amount=Personc['allowed_amountv1']<<16|Personc['allowed_amountv2']
                    sa=Person(user = Personc['user'],
                              username = Personc['username'],
                              nickname = Personc['nickname'],
                              id_number = Personc['id_number'],
                              id_start_date = Personc['id_start_date'],
                              id_end_date = Personc['id_end_date'],
                              id_photo1 = Personc['id_photo1'],
                              id_photo2 = Personc['id_photo2'],
                              address = Personc['address'],
                              latitude = Personc['latitude'],
                              longitude = Personc['longitude'],
                              city = Personc['city'],
                              telephone = Personc['telephone'],
                              mobile = Personc['mobile'],
                              email = Personc['email'],
                              post = Personc['post'],
                              mcc = Personc['mcc'],
                              bank_name = Personc['bank_name'],
                              bankuser = Personc['bankuser'],
                              bank_account = Personc['bank_account'],
                              credit_bank = Personc['credit_bank'],
                              credit_card = Personc['credit_card'],
                              edu = Personc['edu'],
                              month_income = Personc['month_income'],
                              month_expense = Personc['month_expense'],
                              allowed_trade = Personc['allowed_trade'],
                              allowed_time = Personc['allowed_time'],
                              allowed_card = Personc['allowed_card'],
                              allowed_currency = Personc['allowed_currency'],
                              allowed_amount = allowed_amount,
                              last_admin = request.user.id)
                    sa.save()
                    return HttpResponseRedirect('/admin/usermanager/person/')
                else:
                    Personc = form.cleaned_data
                    allowed_amount=Personc['allowed_amountv1']<<16|Personc['allowed_amountv2']
                    userlevel = Personc['userlevel']
                    User.objects.filter(id=Personc['user'].id).update(
                            user_level = userlevel
                    )
                    Person.objects.filter(user=Personc['user']).update(
                              username = Personc['username'],
                              nickname = Personc['nickname'],
                              id_number = Personc['id_number'],
                              id_start_date = Personc['id_start_date'],
                              id_end_date = Personc['id_end_date'],
                              id_photo1 = Personc['id_photo1'],
                              id_photo2 = Personc['id_photo2'],
                              address = Personc['address'],
                              latitude = Personc['latitude'],
                              longitude = Personc['longitude'],
                              city = Personc['city'],
                              telephone = Personc['telephone'],
                              mobile = Personc['mobile'],
                              email = Personc['email'],
                              post = Personc['post'],
                              mcc = Personc['mcc'],
                              bank_name = Personc['bank_name'],
                              bankuser = Personc['bankuser'],
                              bank_account = Personc['bank_account'],
                              credit_bank = Personc['credit_bank'],
                              credit_card = Personc['credit_card'],
                              edu = Personc['edu'],
                              month_income = Personc['month_income'],
                              month_expense = Personc['month_expense'],
                              allowed_trade = Personc['allowed_trade'],
                              allowed_time = Personc['allowed_time'],
                              allowed_card = Personc['allowed_card'],
                              allowed_currency = Personc['allowed_currency'],
                              allowed_amount = allowed_amount,
                              last_admin = request.user.id)
                    return HttpResponseRedirect('/admin/usermanager/person/')
                


#class TerminalBindForm(forms.ModelForm)
#    class Meta:
#        model = TerminalBind

class TerminalBindAdmin(admin.ModelAdmin):
    list_display = ('user','display_userid','terminalid','psamid','tckkey','pinkey1','mackey','diskey','fackey','state')
    search_fields = ['user__id','user__username','terminalid','mackey']
    raw_id_fields = ('user',)
    list_filter = ('state',)
    actions = [export_as_xls]
    
    def user_bind_view(self,request):
        '''
        绑定读卡器自定义实现views
        '''
        errorMsg = None
        if request.method == 'POST':
            try:
                uid,terminals = request.POST.get('userid',0),request.POST.get('selectedTerminalId','')
                user = None
                #pdb.set_trace()
                try:user = User.objects.get(username=uid)
                except:raise Exception(u'不存在登录名为%s的用户' % uid)
                idindex=[id for id in terminals.split(',') if len(id)>0]
                for terminalId in idindex:
                    #print terminalId
                    t = Terminal.objects.get(pk=terminalId)
                    if t.used == TerminalUsedState.AssignedPasm \
                        and t.state == TerminalState.Normal:
                        psam = Psam.objects.get(psamid=t.psamid)
                        tb = TerminalBind.objects.create(user = user,
                                                         udid = user.username,
                                                         terminalid = t.terminalid,
                                                         psamid=psam.psamid,
                                                         psamtp = psam.psamtp,
                                                         tckkey = t.tck,
                                                         pinkey1 = psam.pinkey1,
                                                         pinkey2 = psam.pinkey2,
                                                         mackey = psam.mackey,
                                                         diskey = psam.diskey,
                                                         fackey = u'%s%s' % (psam.producer,psam.model),
                                                         ) 
                        if tb.pk > 0:
                            t.user = user.id
                            t.used = TerminalUsedState.AssignedUser
                            t.save()
                        else:
                            raise Exception(u'save teminalbind error!')
                return HttpResponseRedirect("/admin/core/terminalbind/")
            except Exception,e:
                errorMsg = e.message
        
        terminals = Terminal.objects.filter(used=TerminalUsedState.AssignedPasm,state=TerminalState.Normal)[0:20]
        return render_to_response('admin/usermanager/terminalbind/terminal_bind.html',
                    {'terminals':terminals,
                     'errorMsg':errorMsg},
                    context_instance=RequestContext(request)
            )
    
    def get_terminal(self,request):
        if request.method == 'GET':
            #pdb.set_trace()
            t_num = request.GET.get('terminal_num',None)
            searchResult = Terminal.objects.filter(terminalid=t_num,
                                                   used=TerminalUsedState.AssignedPasm,
                                                   state=TerminalState.Normal)
            if len(searchResult) == 1:
                t = searchResult[0]
                return HttpResponse(json.dumps({'resultCode':'200',
                                                't_id':t.id,
                                                't_num':t.terminalid}))
            else:
                return HttpResponse(json.dumps({'resultCode':'404',
                                                'errMsg':u'搜索到可用读卡器数量为：%s' % len(searchResult)}))
        else:
            raise Exception('http get only!')

    def get_urls(self):
        urls = super(type(self),self).get_urls()

        my_url = patterns('',
            url(r'^bind/$',self.user_bind_view),
            url(r'^getterminal/$',self.get_terminal),
        )
        return my_url + urls;

class SPersonForm(BaseForm):
    class Meta:
        model = SPerson

class SPersonAdmin(BaseAdmin):
    list_display = ('user','display_userid','city','company','nickname','display_user_level','license_number','display_creditratio','display_feeratio','last_modify')
    raw_id_fields = ('user',)
    search_fields = ['user__username','user__id','company']
    list_filter = ('city',)
    actions = [export_as_xls]

    exclude = ('allowed_amount',)

    form=SPersonForm

    def save_model(self,request,obj,form,change):
        if request.method =='POST':
            form=SPersonForm(request.POST)
            if form.is_valid():
                #pdb.set_trace()
                if not change:
                    Personc=form.cleaned_data
                    allowed_amount=Personc['allowed_amountv1']<<16|Personc['allowed_amountv2']
                    sa=SPerson(user = Personc['user'],
                              company = Personc['company'],
                              nickname = Personc['nickname'],
                              legal_person = Personc['legal_person'],
                              id_number = Personc['id_number'],
                              id_stat_date = Personc['id_stat_date'],
                              id_end_date = Personc['id_end_date'],
                              id_photo1 = Personc['id_photo1'],
                              id_photo2 = Personc['id_photo2'],
                              license_number = Personc['license_number'],
                              license_end_date = Personc['license_end_date'],
                              license_photo = Personc['license_photo'],
                              tax_number = Personc['tax_number'],
                              tax_end_date = Personc['tax_end_date'],
                              tax_photo = Personc['tax_photo'],
                              orgcode = Personc['orgcode'],
                              business_addr = Personc['business_addr'],
                              latitude = Personc['latitude'],
                              longitude = Personc['longitude'],
                              city = Personc['city'],
                              contact = Personc['contact'],
                              telephone = Personc['telephone'],
                              mobile = Personc['mobile'],
                              email = Personc['email'],
                              post = Personc['post'],
                              mcc = Personc['mcc'],
                              bankname = Personc['bankname'],
                              bankuser = Personc['bankuser'],
                              bankaccount = Personc['bankaccount'],
                              creditbank = Personc['creditbank'],
                              creditcard = Personc['creditcard'],
                              month_turnover = Personc['month_turnover'],

                              allowed_trade = Personc['allowed_trade'],
                              allowed_time = Personc['allowed_time'],
                              allowed_card = Personc['allowed_card'],
                              allowed_currency = Personc['allowed_currency'],
                              allowed_amount = allowed_amount,
                              last_admin = request.user.id)
                    sa.save()
                    return HttpResponseRedirect('/admin/usermanager/sperson/')
                else:
                    Personc = form.cleaned_data
                    allowed_amount=Personc['allowed_amountv1']<<16|Personc['allowed_amountv2']
                    userlevel = Personc['userlevel']
                    User.objects.filter(id=Personc['user'].id).update(
                            user_level = userlevel
                    )
                    SPerson.objects.filter(user=Personc['user']).update(
                              company = Personc['company'],
                              nickname = Personc['nickname'],
                              legal_person = Personc['legal_person'],
                              id_number = Personc['id_number'],
                              id_stat_date = Personc['id_stat_date'],
                              id_end_date = Personc['id_end_date'],
                              id_photo1 = Personc['id_photo1'],
                              id_photo2 = Personc['id_photo2'],
                              license_number = Personc['license_number'],
                              license_end_date = Personc['license_end_date'],
                              license_photo = Personc['license_photo'],
                              tax_number = Personc['tax_number'],
                              tax_end_date = Personc['tax_end_date'],
                              tax_photo = Personc['tax_photo'],
                              orgcode = Personc['orgcode'],
                              business_addr = Personc['business_addr'],
                              latitude = Personc['latitude'],
                              longitude = Personc['longitude'],
                              city = Personc['city'],
                              contact = Personc['contact'],
                              telephone = Personc['telephone'],
                              mobile = Personc['mobile'],
                              email = Personc['email'],
                              post = Personc['post'],
                              mcc = Personc['mcc'],
                              bankname = Personc['bankname'],
                              bankuser = Personc['bankuser'],
                              bankaccount = Personc['bankaccount'],
                              creditbank = Personc['creditbank'],
                              creditcard = Personc['creditcard'],
                              month_turnover = Personc['month_turnover'],

                              allowed_trade = Personc['allowed_trade'],
                              allowed_time = Personc['allowed_time'],
                              allowed_card = Personc['allowed_card'],
                              allowed_currency = Personc['allowed_currency'],
                              allowed_amount = allowed_amount,
                              last_admin = request.user.id)
                    return HttpResponseRedirect('/admin/usermanager/sperson/')


class MerchantForm(BaseForm):

    class Meta:
        model = Merchant
    
class MerchantAdmin(BaseAdmin):
    list_display = ('user', 'display_userid','city','company','nickname','display_user_level','id_number','license_number','display_creditratio','display_feeratio','last_modify')
    raw_id_fields = ('user',)
    search_fields = ['user__username','user__id','company']
    list_filter = ('city',)
    actions = [export_as_xls]
    
    exclude = ('allowed_amount',)

    form=MerchantForm

    def save_model(self,request,obj,form,change):
        if request.method =='POST':
            form=MerchantForm(request.POST)
            if form.is_valid():
                #pdb.set_trace()
                if not change:
                    Personc=form.cleaned_data
                    allowed_amount=Personc['allowed_amountv1']<<16|Personc['allowed_amountv2']
                    sa=Merchant(user = Personc['user'],
                              company = Personc['company'],
                              nickname = Personc['nickname'],
                              legal_person = Personc['legal_person'],
                              id_number = Personc['id_number'],
                              id_stat_date = Personc['id_stat_date'],
                              id_end_date = Personc['id_end_date'],
                              id_photo1 = Personc['id_photo1'],
                              id_photo2 = Personc['id_photo2'],
                              license_number = Personc['license_number'],
                              license_end_date = Personc['license_end_date'],
                              license_photo = Personc['license_photo'],
                              tax_number = Personc['tax_number'],
                              tax_end_date = Personc['tax_end_date'],
                              tax_photo = Personc['tax_photo'],
                              orgcode = Personc['orgcode'],
                              business_addr = Personc['business_addr'],
                              latitude = Personc['latitude'],
                              longitude = Personc['longitude'],
                              city = Personc['city'],
                              contact = Personc['contact'],
                              telephone = Personc['telephone'],
                              mobile = Personc['mobile'],
                              email = Personc['email'],
                              post = Personc['post'],
                              mcc = Personc['mcc'],
                              bankname = Personc['bankname'],
                              bankuser = Personc['bankuser'],
                              bankaccount = Personc['bankaccount'],
                              creditbank = Personc['creditbank'],
                              creditcard = Personc['creditcard'],
                              month_turnover = Personc['month_turnover'],

                              allowed_trade = Personc['allowed_trade'],
                              allowed_time = Personc['allowed_time'],
                              allowed_card = Personc['allowed_card'],
                              allowed_currency = Personc['allowed_currency'],
                              allowed_amount = allowed_amount,
                              last_admin = request.user.id)
                    sa.save()
                    return HttpResponseRedirect('/admin/usermanager/merchant/')
                else:
                    Personc = form.cleaned_data
                    allowed_amount=Personc['allowed_amountv1']<<16|Personc['allowed_amountv2']
                    userlevel = Personc['userlevel']
                    User.objects.filter(id=Personc['user'].id).update(
                            user_level = userlevel
                    )
                    Merchant.objects.filter(user=Personc['user']).update(
                              company = Personc['company'],
                              nickname = Personc['nickname'],
                              legal_person = Personc['legal_person'],
                              id_number = Personc['id_number'],
                              id_stat_date = Personc['id_stat_date'],
                              id_end_date = Personc['id_end_date'],
                              id_photo1 = Personc['id_photo1'],
                              id_photo2 = Personc['id_photo2'],
                              license_number = Personc['license_number'],
                              license_end_date = Personc['license_end_date'],
                              license_photo = Personc['license_photo'],
                              tax_number = Personc['tax_number'],
                              tax_end_date = Personc['tax_end_date'],
                              tax_photo = Personc['tax_photo'],
                              orgcode = Personc['orgcode'],
                              business_addr = Personc['business_addr'],
                              latitude = Personc['latitude'],
                              longitude = Personc['longitude'],
                              city = Personc['city'],
                              contact = Personc['contact'],
                              telephone = Personc['telephone'],
                              mobile = Personc['mobile'],
                              email = Personc['email'],
                              post = Personc['post'],
                              mcc = Personc['mcc'],
                              bankname = Personc['bankname'],
                              bankuser = Personc['bankuser'],
                              bankaccount = Personc['bankaccount'],
                              creditbank = Personc['creditbank'],
                              creditcard = Personc['creditcard'],
                              month_turnover = Personc['month_turnover'],

                              allowed_trade = Personc['allowed_trade'],
                              allowed_time = Personc['allowed_time'],
                              allowed_card = Personc['allowed_card'],
                              allowed_currency = Personc['allowed_currency'],
                              allowed_amount = allowed_amount,
                              last_admin = request.user.id)
                    return HttpResponseRedirect('/admin/usermanager/merchant/')

    
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name','zmk','zpk','mcc','chcd','inscd', 'code', 'regioncd','mchntid')

class ChannelUserAdmin(admin.ModelAdmin):
    list_display = ('userid', 'chnlid', 'chnluserid', 'chnltermid', 'chnlusernm','mcc')
    search_fields = ('userid',)

class ChargeAdmin(MisDBModelAdmin):
    search_fields = ['userid']
    list_display = ('id','userid','display_type','display_status','desc','fee','transformat_sucesstime')

class InvoiceAdmin(admin.ModelAdmin):
    #list_display = ('buyerid','orderformtype','buyername','buyercontactmethod','buyeraddress','buytype','paymoney','terminalcount','paystate','former','producetime','auditstate','auditer')

    list_display = ('orderid','auditer')
    def change_view(self,request,object_id,extra_context=None):
        self.fields = ('orderformtype','buyerid','buyername','buyercontactmethod','buyeraddress','buytype','paymoney','terminalcount','paystate','former','producetime','auditstate')
        return super(type(self),self).change_view(request,object_id,extra_context)

    def add_view(self,request):
        self.fields = ('orderformtype','buyerid','buyername','buyercontactmethod','buyeraddress','buytype','paymoney','terminalcount','paystate')
        return super(type(self),self).add_view(request)

    def save_model(self,request,obj,form,change): 
        #import pdb
        #pdb.set_trace()
        if form.is_valid():
            invo = form.save(commit=False)
            if change:
                if invo.auditstate == 3:
                    invosa = Invoice.objects.get(id = obj.id)
                    if invosa.auditstate != 3:
                        invosa.auditer = request.user.id
                        invosa.auditstate = 3
                        invosa.save()
            else:
                orderidindex = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                record = Invoice.objects.filter(orderid__contains=orderidindex).order_by('-id')
                if record.count()>0:
                    last = int(record[0].orderid[14:])
                    last += 1
                    orderid = orderidindex+str(last).zfill(4)
                else:
                    orderid = orderidindex+'0001'
                invosa = Invoice(orderformtype = invo.orderformtype,
                                orderid = orderid,
                                buyerid = invo.buyerid,
                                buyername = invo.buyername,
                                buyercontactmethod = invo.buyercontactmethod,
                                buyeraddress = invo.buyeraddress,
                                buytype = invo.buytype,
                                paymoney = invo.paymoney,
                                terminalcount = invo.terminalcount,
                                paystate = invo.paystate,
                                former = request.user.id,
                                producetime = datetime.datetime.now(),
                                auditstate = 1,
                                auditer = '',
                                )
                invosa.save()
               

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','display_userid','nickname','type','provision','province','city','groupid','terminalcount','banktype','bankname','bankuser','bankaccount','mobile','allowarea','businessaddr','address','post','telephone','email','area','logisticaddr','tid','mcc','org_code','last_modify','last_admin','longitude','latitude','is_developer','memo','name','idnumber','idenddate','needauth','licensenumber','legalperson','licenseend_date','taxnumber','contact','passcheck','founddate',)
    raw_id_fields = ('user',)

admin.site.register(Profile,ProfileAdmin)  
admin.site.register(Invoice,InvoiceAdmin)
admin.site.register(Person,PersonAdmin)
admin.site.register(SPerson, SPersonAdmin)
admin.site.register(Merchant, MerchantAdmin)
admin.site.register(TerminalBind,TerminalBindAdmin)
admin.site.register(ChannelUser, ChannelUserAdmin)
admin.site.register(Recharge,ChargeAdmin)

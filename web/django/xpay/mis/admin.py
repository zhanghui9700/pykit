#!/usr/bin/env python
#coding=utf-8
import pdb,os,datetime

from django import forms
from django.http import HttpResponseRedirect,HttpResponse
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.forms.extras.widgets import SelectDateWidget
from models import Psam,Terminal,OpLog
from util.define import TerminalState,TerminalUsedState,PsamState,PsamUsedState
import datetime
from django.conf.urls.defaults import patterns,url
from django.shortcuts import render_to_response
from django.template import RequestContext
from util.multidb_admin import CoreDBTabularInline,UserInline,MisDBModelAdmin

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

from util.tools import csv2terminal,csv_readlines
from util.multidb_admin import CoreDBModelAdmin
csrf_protect_m = method_decorator(csrf_protect)


class PsamForm(forms.ModelForm):

    def save(self,commit=True):
        return super(PsamForm,self).save(commit=False)

    class Meta:
        model=Psam

class PsamAddForm(forms.Form):
    PSAMTP_CHOICES=(
        ('21',u'钱方3des'),
        ('22',u'富友3des'),
    )
    PRODUCER_CHOICES=(
        ('0001',u'艾创'),
    )
    MODEL_CHOICES=(
        ('0001',u'psam'),
    )
    STATE_CHOICES=(
        (0,u'正常'),
        (1,u'已维修'),
        (2,u'报废'),
    )

    my_errors={'required':u'输入不能为空'}

    psamidstart=forms.CharField(max_length=8,label=_('PSAM开始卡号'),required=True,widget=forms.TextInput(attrs={'class':'text a1 a5'}),error_messages=my_errors)
    psamidend=forms.CharField(max_length=8,label=_('PSAM结束卡号'),required=True,widget=forms.TextInput(attrs={'class':'text a1 a5'}),error_messages=my_errors)
    psamtp=forms.ChoiceField(required=True,choices=PSAMTP_CHOICES,widget=forms.Select(attrs={'class':'text x3'}),error_messages=my_errors)
    producer=forms.ChoiceField(required=True,choices=PRODUCER_CHOICES,widget=forms.Select(attrs={'class':'text x4'}),error_messages=my_errors)
    model=forms.ChoiceField(required=True,choices=MODEL_CHOICES,widget=forms.Select(attrs={'class':'text x3'}),error_messages=my_errors)
    produce_date=forms.DateTimeField(label=_('生产日期'),widget=SelectDateWidget(attrs={'class':'text x3'},years=range(2010,datetime.datetime.now().year+10)),required=True,error_messages=my_errors)
    pinkey1=forms.CharField(max_length=32,label=_('PINKEY1'),initial='FC003F7139AEA8AA85F89319C0333658',required=True,widget=forms.TextInput(attrs={'class':'text a1 a5','style':'width:20em;'}),error_messages=my_errors)
    pinkey2=forms.CharField(max_length=32,label=_('PINKEY2'),initial='97F30539FF3CA379FE4C606608D5A128',required=True,widget=forms.TextInput(attrs={'class':'text a1 a5','style':'width:20em;'}),error_messages=my_errors)
    mackey=forms.CharField(max_length=32,label=_('MACKEY'),initial='DD090BA53E64C6B00462CDDBB30FC857',required=True,widget=forms.TextInput(attrs={'class':'text a1 a5','style':'width:20em;'}),error_messages=my_errors)
    diskey=forms.CharField(max_length=32,label=_('DISKEY'),initial='65600001',required=True,widget=forms.TextInput(attrs={'class':'text a1 a5','style':'width:20em;'}),error_messages=my_errors)
    state=forms.ChoiceField(required=True,choices=STATE_CHOICES,widget=forms.Select(attrs={'class':'text x4'}),error_messages=my_errors)

    def clean_psamidstart(self):
        psam_num = self.data.get('psamidstart')
        if len(psam_num) != 8:
            raise forms.ValidationError(u'PSAM ID必须为8字符')   
        try:
            psam_num = int(psam_num)
        except:
            raise forms.ValidationError(u'PSAM ID转换为数字失败')
        self.startid=psam_num
        return psam_num

    def clean_psamidend(self):
        psam_num = self.data.get('psamidend')
        if len(psam_num) != 8:
            raise forms.ValidationError(u'PSAM ID必须8为字符') 
        try:
            psam_num = int(psam_num)
        except:
            raise forms.ValidationError(u'PSAM ID转换为数字失败')
        self.endid=psam_num
        if self.cleaned_data['psamidstart'] > psam_num:
            raise forms.ValidationError(u'PSAM 起始ID大于结束ID')
        
        psams = range(self.cleaned_data['psamidstart'],psam_num + 1)
        psamIDs = [u'%06d'% id for id in psams]
        self.psamList = []

        for psamID in psamIDs:
            p = Psam.objects.filter(psamid=psamID)
            if p.count() != 0:
                raise forms.ValidationError(u'PSAM ID:%s 已存在' % psamID)
            self.psamList.append(p)
        return psam_num

class PsamAdmin(admin.ModelAdmin):
    list_display = ('psamid','terminalid','psamtp','used','state','advice')
    list_filter = ('used','state') 
    form=PsamForm
     
    add_form_template = u'admin/mis/psam_input.html'
    add_form = PsamAddForm
    
    def add_view(self,request):
        if request.method == 'POST':
            form=PsamAddForm(request.POST)
            if form.is_valid():
                #pdb.set_trace()
                cd=form.cleaned_data                
                start=int(cd['psamidstart'])
                end=int(cd['psamidend'])
                for i in range(start,end+1):
                    p=Psam(psamid=i,
                           psamtp=cd['psamtp'],
                           producer=cd['producer'],
                           model=cd['model'],
                           produce_date=cd['produce_date'],
                           pinkey1=cd['pinkey1'],
                           pinkey2=cd['pinkey2'],
                           mackey=cd['mackey'],
                           diskey=cd['diskey'],
                           used = 0, state = cd['state'],
                           last_modify=datetime.datetime.now(),
                           last_admin = request.user.id)
                    p.save()
                msg = u'管理员[%s]添加psam初始号[%s]psam结束号[%s]'%(request.user.id,start,end)
                OpLog.objects.log_action(request.user.id,4,u'添加客户端',msg)
                return HttpResponseRedirect('/admin/mis/psam/')                
        
        return super(PsamAdmin,self).add_view(request)

    def change_view(self,request,object_id,extra_context=None):
        self.exclude = ('last_modify','last_admin')
        return super(type(self),self).change_view(request,object_id,extra_context)
    
    def save_model(self,request,obj,form,change):
        if change:
            if form.is_valid():
                psam = form.save(commit=False)
                psam.last_admin = request.user.id
                psam.save()
            
    def get_form(self,request,obj=None,**kwargs):
        if obj is None:
            return self.add_form
        return super(PsamAdmin,self).get_form(request,obj,**kwargs)

class TerminalChangeForm(forms.ModelForm):
    class Meta:
        model=Terminal
        exclude = ('last_modify','last_admin','user',)

    def save(self,commit=True):
        return super(TerminalChangeForm,self).save(commit=False)

class TerminalForm(forms.ModelForm):
    PRODUCER_CHOICES=(
        ('0001',u'艾创'),
        ('0002',u'鼎合'),
    )

    MODEL_CHOICES=(
        ('0001',u'qpos'),
        ('0002',u'ipos'),
    )

    startid = forms.CharField(max_length=20,required=True,label=u'读卡器起始ID',help_text=u'20位字符串，后6位必须能转换成Int32',widget=forms.TextInput(attrs={'style':'width:20em'}))
    endid = forms.CharField(max_length=20,required=True,label=u'读卡器结束ID',help_text=u'20位字符串，后6位必须能转换成Int32', widget=forms.TextInput(attrs={'style':'width:20em'})) 
    psamStartID = forms.CharField(max_length=8,required=True,label=u'PSAM起始ID',help_text=u'8位字符必须能转换成Int32')
    psamEndID = forms.CharField(max_length=8,required=True,label=u'PSAM结束ID',help_text=u'8位字符必须能转换成Int32')
    tck = forms.CharField(max_length=32,required=True,initial='0EA08C852B9653F76DB4A90612850CBD',widget=forms.TextInput(attrs={'style':'width:20em;'}))
    produce_date=forms.DateTimeField(label=_('生产日期'),widget=SelectDateWidget(attrs={'class':'text x3'},years=range(2010,datetime.datetime.now().year+10)),required=True)
    producer=forms.ChoiceField(required=True,choices=PRODUCER_CHOICES,initial='0001',widget=forms.Select(attrs={'class':'text x4'}))
    model=forms.ChoiceField(required=True,choices=MODEL_CHOICES,initial='0001',widget=forms.Select(attrs={'class':'text x3'}))
    file=forms.FileField(required=False,label=u'上传读卡器csv',help_text=u'csv格式:terminalid,psamid')

    class Meta:
        model = Terminal
        fields = ('producer','model','produce_date','tck','state',)

    def clean_startid(self):
        start = self.data.get('startid')
        if len(start) != 20:
            raise forms.ValidationError(u'读卡器ID必须20位字符')

        startNumber = start[14:]
        try:
            startNumber = int(startNumber)
        except:
            raise forms.ValidationError(u'读卡器ID后6位无法转换成数字')
        return startNumber

    def clean_endid(self):
        end = self.data.get('endid')
        if len(end) != 20:
            raise forms.ValidationError(u'读卡器ID必须20位字符')

        endNumber = end[14:]
        try:
            endNumber = int(endNumber)
        except:
            raise forms.ValidationError(u'读卡器ID后6位无法转换成数字')

        if self.cleaned_data['startid'] > endNumber:
            raise forms.ValidationError(u'读卡器结束ID必须大于起始ID')

        terminals = range(self.cleaned_data['startid'],endNumber+1)
        terminalIDs = [u'%s%06d' % (end[:14],id) for id in terminals]
        self.terminalList = []
    
        #pdb.set_trace()
        for terminalId in terminalIDs:
            tm = Terminal.objects.filter(terminalid = terminalId)
            if tm.count() != 0:
                raise forms.ValidationError(u'读卡器ID:%s 已录入'% terminalId)

            self.terminalList.append(terminalId)

        print self.terminalList
        return endNumber

    def clean_psamStartID(self):
        psam_num = self.data.get('psamStartID')
        if len(psam_num) != 8:
            raise forms.ValidationError(u'PSAM ID必须8为字符')   
        try:
            psam_num = int(psam_num)
        except:
            raise forms.ValidationError(u'PSAM ID转换为数字失败')

        return psam_num

    def clean_psamEndID(self):
        psam_num = self.data.get('psamEndID')
        if len(psam_num) != 8:
            raise forms.ValidationError(u'PSAM ID必须8为字符') 
        try:
            psam_num = int(psam_num)
        except:
            raise forms.ValidationError(u'PSAM ID转换为数字失败')
        
        if self.cleaned_data['psamStartID'] > psam_num:
            raise forms.ValidationError(u'PSAM 起始ID大于结束ID')
        
        psams = range(self.cleaned_data['psamStartID'],psam_num + 1)
        psamIDs = [u'%06d'% id for id in psams]
        self.psamList = []

        for psamID in psamIDs:
            try:
                p = Psam.objects.get(psamid=psamID)
            except:
                raise forms.ValidationError(u'PSAM ID:%s 不存在' % psamID)

            if p.used != PsamUsedState.InWarehouse or p.state != PsamState.Normal:
                raise forms.ValidationError(u'PSAM ID:%s 已经被使用' % psamID)

            self.psamList.append(p)

        if len(self.terminalList) != len(self.psamList):
            raise forms.ValidationError(u'读卡器数量：%s，PSAM数量：%s'%(len(self.terminalList),len(self.psamList)))

        print self.psamList
        return psam_num

    def save(self,commit=True):
        t = super(TerminalForm,self).save(commit=False)
        t.psams = self.psamList
        t.terminalIDs = self.terminalList
        return t

 
class TerminalAdmin(admin.ModelAdmin):
    list_display = ('user','terminalid','psamid','model','tck','used','state')
    list_filter = ('used','state')
    search_fields = ['terminalid','psamid'] 
    add_form = TerminalForm
    #add_form_template = u'admin/mis/terminal_input.html'

    form=TerminalChangeForm
    
    def add_view(self,request):
        if request.method =='POST':
            if request.FILES.get('file'):
                n = csv2terminal(request.FILES.get('file'))
                messages.add_message(request, messages.INFO, u'成功批量导入%s个读卡器'%n)
                return HttpResponseRedirect('/admin/mis/terminal/')
                
            form = TerminalForm(request.POST)
            if form.is_valid():
                tmiObj = form.save(commit=False)
                if tmiObj is not None:
                    for tid,psamObj in zip(tmiObj.terminalIDs,tmiObj.psams):
                        t = Terminal.objects.create(
                            terminalid = tid,
                            psamid = psamObj.psamid,
                            producer = tmiObj.producer,
                            model = tmiObj.model,
                            produce_date = tmiObj.produce_date,
                            tck = tmiObj.tck,
                            used = 1,
                            state = TerminalState.Normal,
                            last_admin = request.user.id,
                        )    
                        if t.pk > 0:
                            psamObj.used = PsamUsedState.Assigned
                            psamObj.terminalid = tid
                            psamObj.save()
                msg = u'管理员[%s]添加psam卡号[%s]terminal[%s]'%(request.user.id,psamObj.psamid,tid)
                OpLog.objects.log_action(request.user.id,4,u'添加客户端',msg)
                return HttpResponseRedirect('/admin/mis/terminal/')
            else:
                return super(TerminalAdmin,self).add_view(request)
        else:
            return super(TerminalAdmin,self).add_view(request)

    def change_view(self,request,object_id,extra_context=None):
        return super(type(self),self).change_view(request,object_id,extra_context)

    def save_model(self,request,obj,form,change):
        if change:
            if form.is_valid():    
                terminal = form.save(commit=False)
                terminal.last_admin = request.user.id
                terminal.save()

    def get_form(self,request,obj=None,**kwargs):
        if obj is None:
            return self.add_form
        return super(TerminalAdmin,self).get_form(request,obj,**kwargs)
    
    def terminal_outbound(self,request,extra_context=None):
        errorMsg = None
        if request.method == 'POST':
            try:
                if 'csvfile' in request.FILES:
                    file = request.FILES['csvfile']
                    if os.path.splitext(file._name)[1].lower() != '.csv':
                        raise Exception(u'亲！文件扩展名错误，请上传csv文件！')
                    lines = csv_readlines(request.FILES.get('csvfile'))
                    counter = 0
                    for item in lines and lines or []:
                        if item and len(item) == 2:
                            t = Terminal.objects.filter(terminalid=item[0])
                            if t.count() > 0:
                                counter += t.update(group_id=item[1],
                                                    last_admin=request.user.id,
                                                    last_modify = datetime.datetime.now(),
                                                    advice=u'批量出库:%s'%item[1])
                        else:
                            raise Exception('csv文件错误，读取数据不符合规范！')
                            
                    messages.add_message(request, messages.INFO, u'批量出库%s个读卡器'%counter)
                    return HttpResponseRedirect('/admin/mis/terminal/')
            except Exception,ex:
                errorMsg = ex.message
        
        context = {
            'errorMsg':errorMsg
        }
        return render_to_response('admin/mis/terminal/terminal_outbound.html',context,context_instance=RequestContext(request)) 

    def get_urls(self):
        from django.conf.urls.defaults import patterns,url
        custom_urls = patterns('',
            url(r'^outbound/$',self.terminal_outbound,name='terminal_batch_outbound'),
        )
        return custom_urls + super(type(self),self).get_urls() 
class OpLogAdmin(MisDBModelAdmin):
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

admin.site.register(Psam,PsamAdmin)
admin.site.register(Terminal, TerminalAdmin)
admin.site.register(OpLog,OpLogAdmin)

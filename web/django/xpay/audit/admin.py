#!/usr/bin/env python
#coding=utf-8
import pdb,datetime,random
import os,uuid,json

from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib import databrowse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect,HttpResponse
from django import forms
from django.db import transaction
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages

from pyExcelerator import *

from models import Apply, ApplyCode, VerifyCode,Upgrade,AuditLog,UpgradeVoucher,OpLog
from core.models import Person,SPerson,Merchant,UserProxy
from util.define import UserState,ApplyState,LICENSE_TYPE,UPGRADE_IMAGE
from forms import ApplyPassForm
from trade.models import Channel
from util.imgstore import save_image
from util.multidb_admin import CoreDBTabularInline,UserInline,MisDBModelAdmin
from util.tools import csv_readlines

from util.sendsms import sendsmsv2

CHOICES_TERMINAL_COUNT = (
    (1,'1'),
    (2,'2'),
    (3,'3'),
    (4,'4'),
    (5,'5'),
)

import logging
_log = logging.getLogger('my_info')

def gen_applycode(str):
    '''
    s = md5.new(str).hexdigest()
    s1 = hex(int(s[0:8],16)+int(s[8:16],16)+int(s[16:24],16)+int(s[24:32],16))
    return s1[-8:]
    '''
    code = random.randint(10000000,99999999) 
    while ApplyCode.objects.filter(code=code).count() > 0:
        code = random.randint(10000000,99999999)
    return code


class ApplyForm(forms.ModelForm):
    password = forms.CharField(max_length=16, label=u'初始密码', required=True, widget=forms.PasswordInput(attrs={'value':'123456'}))
    terminalcount = forms.IntegerField(label=u'读卡器数量',widget=forms.Select(choices=CHOICES_TERMINAL_COUNT))
    logisticaddr = forms.CharField(max_length=256,label=u'配送地址',widget=forms.Textarea(),required=False)
    
    id_front = forms.ImageField(label=u'身份证正面',max_length=256,required=False)
    id_back = forms.ImageField(label=u'身份证反面',max_length=256,required=False)
    tax = forms.ImageField(label=u'税务登记证',max_length=256,required=False)
    license_page1 = forms.ImageField(label=u'营业执照照片(到期日期(第一页))',max_length=256,required=False)
    license_page2 = forms.ImageField(label=u'营业执照照片(年检章(第一页))',max_length=256,required=False)
    org_code = forms.ImageField(label=u'组织机构代码证',max_length=256,required=False)
    contract = forms.ImageField(label=u'租赁合同证明(公司地址)',max_length=256,required=False) 
    contract2 = forms.ImageField(label=u'租赁合同证明(到期日期)',max_length=256,required=False) 
    contract3 = forms.ImageField(label=u'租赁合同证明(合同描述)',max_length=256,required=False) 
    gathering_attest = forms.ImageField(label=u'收款需求证明',max_length=256,required=False)
    business_attest_front = forms.ImageField(label=u'营业场地证明',max_length=256,required=False)
    business_attest_other2 = forms.ImageField(label=u'营业场地证明2',max_length=256,required=False)
    business_attest_other3 = forms.ImageField(label=u'营业场地证明3',max_length=256,required=False)
    business_attest_other4 = forms.ImageField(label=u'营业场地证明4',max_length=256,required=False)
    business_attest_other5 = forms.ImageField(label=u'营业场地证明5',max_length=256,required=False)
    business_attest_other6 = forms.ImageField(label=u'营业场地证明6',max_length=256,required=False)
    business_attest_other7 = forms.ImageField(label=u'营业场地证明7',max_length=256,required=False)
    open_license = forms.ImageField(label=u'开户许可证明',max_length=256,required=False)
    apply_number = forms.ImageField(label=u'申请台数证明',max_length=256,required=False)
    user_bank_card = forms.ImageField(label=u'银行卡正反面',max_length=256,required=False)
    payed_tax = forms.ImageField(label=u'完税证明',max_length=256,required=False)
    legal_person_auth = forms.ImageField(label=u'法人授权书',max_length=256,required=False)
    legal_person_auth_front = forms.ImageField(label=u'授权法人身份证正面',max_length=256,required=False) 
    legal_person_auth_back = forms.ImageField(label=u'授权法人身份证反面',max_length=256,required=False)
    other_voucher = forms.ImageField(label=u'其他信用凭证',max_length=256,required=False)
    photo1 = forms.ImageField(label=u'其他信用凭证',max_length=256,required=False)
    photo0 = forms.ImageField(label=u'其他信用凭证',max_length=256,required=False)
    photo2 = forms.ImageField(label=u'其他信用凭证',max_length=256,required=False)
    photo3 = forms.ImageField(label=u'其他信用凭证',max_length=256,required=False)
    photo4 = forms.ImageField(label=u'其他信用凭证',max_length=256,required=False)
    auditinfo = forms.CharField(label=u'审核信息',max_length=256,required=False,help_text=u'审核信息，这个字段只需要审核失败时填写申请失败原因即可！',widget=forms.Textarea())
    def clean_password(self):
        pwd = self.get_field_value('password',u'请输入初始密码!')
        if len(pwd) < 6 or len(pwd) > 16:
            raise forms.ValidationError(u'请输入6~16位的有效密码')

        return pwd

    def clean_mobile(self):
        _m = self.get_field_value('mobile',u'请输入要注册的手机号!')
        try:
            u = User.objects.filter(username=_m)
            if len(u) > 0:
                raise
        except:raise forms.ValidationError(u'手机号"%s"已注册' % _m)
        
        return _m

    def clean_name(self):
        return self.get_field_value('name',u'用户名不能为空!')

    def clean_contact(self):
        return self.get_field_value('contact',u'联系人不能为空!')
    
    def clean_bankname(self):
        return self.get_field_value('bankname',u'开户银行名称不能为空!')
    
    def clean_bankuser(self):
        return self.get_field_value('bankuser',u'开户人姓名不能为空!')
     
    def clean_bankaccount(self):
        return self.get_field_value('bankaccount',u'银行卡号不能为空!')
    
    def clean_idnumber(self):
        return self.get_field_value('idnumber',u'法人身份证不能为空!')
    
    def clean_legalperson(self):
        return self.get_field_value('legalperson',u'法人姓名不能为空!')
    
    def clean_address(self):
        return self.get_field_value('address',u'注册地址不能为空!')
    
    def clean_post(self):
        return self.get_field_value('post',u'邮政编码不能为空!')
    
    def clean_businessaddr(self):
        return self.get_field_value('businessaddr',u'经营地址不能为空!')

    def get_field_value(self,inputName,errMsg=None):
        _value = self.data.get(inputName,None)
        if _value is None or len(_value) == 0:
            raise forms.ValidationError(errMsg)

        return _value

    class Meta:
        model = Apply
        fileds = ('password',)

def apply_passed_action(modeladmin, request, queryset):
    '''将选中的用户审核为通过状态,admin action'''
    passedApply = []
    for record in [item for item in queryset \
                        if item.state == ApplyState.WAIT_AUDIT \
                                or item.state == ApplyState.WAIT_REAUDIT]:
        if record.audit_passed(request.user.id) > 0:
            passedApply.append(record)
    
    if len(passedApply) == 0:
        messages.error(request,u'没有用户被审核通过') 
        return HttpResponseRedirect(u'/admin/%s/%s' % (Apply._meta.app_label.lower(),Apply.__name__.lower()))
    
    context = {
        'queryset':passedApply,
        'forms':ApplyPassForm(),
        'opts':Apply._meta,
    } 
    return render_to_response('admin/audit/apply/apply_pass.html',context,context_instance=RequestContext(request))
apply_passed_action.short_description = u'审核通过'

class ApplyAdmin(MisDBModelAdmin):
    list_display = ('user','display_user_name','name','nickname','uploadtime','usertype','idnumber', 'display_auditinfo','state','groupid',)
    search_fields = ('user','name',)
    list_filter = ('state','groupid',)
    #actions = [apply_passed_action]
    form = ApplyForm 
    
    def get_object(self,request,object_id):
        obj = super(type(self),self).get_object(request,object_id)
        if obj and obj.ext and len(obj.ext) > 0:
            try:
                _dict = json.loads(obj.ext)
                obj.ext = ''
                for key in _dict.keys():
                    obj.ext += '%s:%s,'%(key,_dict[key])
            except:pass
        
        return obj

    def add_view(self,request):
        self.exclude = ('user','latitude','longitude','monthincome','monthexpense','edu','idphoto1','idphoto2','licensephoto','taxphoto','last_admin','mcc')
        return super(type(self),self).add_view(request)
    
    def save_model(self,request,obj,form,change):
        if form.is_valid():
            apl = form.save(commit=False)
            try:
                sid = transaction.savepoint()
                if not change:
                    u = User.objects.create(username=apl.mobile,
                                        user_type = apl.usertype,
                                        user_level = 1,
                                        email = u'%s@qfpay.com' % apl.mobile,
                                        mobile = apl.mobile,
                                        state = UserState.CREATED 
                                        )
                    u.set_password(form.cleaned_data['password'])
                    u.save()
                    apl.state = ApplyState.WAIT_AUDIT
                    apl.user = u.id 
                apl.save()
                if apl.pk <= 1:
                    raise
                self.save_voucher(request,apl)
                _log.info(u'apl.user:%s,apl.state:%s'%(apl.user,apl.state))
            except Exception,ex:
                transaction.savepoint_rollback(sid)
                raise
            else:
                transaction.savepoint_commit(sid)
    
    def save_voucher(self,request,obj):
        for name in LICENSE_TYPE.IMAGE_TYPE:
            self.save_img_to_nfs(uid=obj.user,
                                 name=name,
                                 file=request.FILES.get(name,None),
                                 type=LICENSE_TYPE.IMAGE_TYPE.get(name,0),
                                 state = request.POST.get('%s_state'%name,UPGRADE_IMAGE.STATE['WAIT_AUDIT']))

    def save_img_to_nfs(self,uid,name,file,type,state=0):
        if file is not None:
            imgName = save_image(uid,name,file)
            qs = UpgradeVoucher.objects.filter(user_id=uid,\
                                            cert_type = type,\
                                            name=imgName)

            if qs.count() == 0:           
                UpgradeVoucher.objects.create(user_id=uid,
                                            cert_type=type,
                                            name=imgName)
        else:
            qs=UpgradeVoucher.objects.filter(user_id=uid,\
                                            cert_type = type,\
                                            name=name+'.jpg')
            qs.update(state=state)
     
    def get_form(self,request,obj=None,**kwargs):
        '''显示凭证和凭证审核结果'''
        for name,field in self.form.base_fields.items():
            if field.__class__ == forms.fields.ImageField:
                self.form.base_fields[name].help_text = u''

        if obj is not None: 
            if obj.provision == ' ':
                obj.provision = obj.mcc
            ls = UpgradeVoucher.objects.filter(user_id=obj.user)
            if ls.count() > 0 or True:
                templet = u'<a href="/preview/%(uid)s/original/%(filename)s" target="_blank">\
                                <img src="/preview/%(uid)s/middle/%(filename)s"/>\
                            </a>\
                            <select name="%(voucher_name)s_state" class="_voucher_result">\
                                <option value="0" %(op_0)s>待审</option>\
                                <option value="1" %(op_1)s>通过</option>\
                                <option value="2" %(op_2)s>不合格</option>\
                                <option value="3" %(op_3)s>不清晰</option>\
                            </select>'
                for item in ls:
                    voucherName = item.name.split('.')[0]
                    if voucherName in self.form.base_fields.keys():
                        op_result = range(0,4)
                        for i in op_result:
                            if item.state == i:
                                op_result[i] = 'selected'
                            else:
                                op_result[i]=''
                        self.form.base_fields[voucherName].help_text = templet %{
                                "uid":obj.user,
                                "filename":item.name,
                                "voucher_name":voucherName,
                                "op_0":op_result[0],
                                "op_1":op_result[1],
                                "op_2":op_result[2],
                                "op_3":op_result[3]
                            }

        return super(type(self),self).get_form(request,obj,**kwargs)
    
    def change_view(self,request,object_id,extra_context=None):
        self.exclude = ('latitude','longitude','monthincome','monthexpense','edu','idphoto1','idphoto2','licensephoto','taxphoto','last_admin','mcc',)
        self.readonly_fields = ('user','mobile','usertype')

        if request.method == 'POST': 
            if 'apply_passed' in request.POST: #审核通过
                record = Apply.objects.get(user=object_id)
                if record.state in[ApplyState.WAIT_AUDIT,\
                                    ApplyState.WAIT_REAUDIT]:
                    passedApply = []
                    if record.audit_passed(request.user.id) > 0:
                        passedApply.append(record)
                
                    if len(passedApply) == 0:
                        messages.error(request,u'没有用户被审核通过') 
                        return HttpResponseRedirect(u'/admin/%s/%s' % (Apply._meta.app_label.lower(),Apply.__name__.lower()))
                
                    context = {
                        'queryset':passedApply,
                        'forms':ApplyPassForm(),
                        'opts':Apply._meta,
                        'usertype':record.usertype,
                    }    
                    
                    msg = u'管理员[%s]审核申请表[%s]通过'%(request.user.id,record.user)
                    OpLog.objects.log_action(request.user.id,1,u'审核通过',msg)
                    messages.info(request,u'商户申请审核通过，设置交易度衡后即可交易！')
                    return render_to_response('admin/audit/apply/apply_pass.html',context,context_instance=RequestContext(request))  
                
                messages.error(request,u"只有待审核或者待复审的申请表可以进行审核！")
                return HttpResponseRedirect(u'/admin/%s/%s/%s/' % (Apply._meta.app_label.lower(),Apply.__name__.lower(),object_id))
            
            if 'apply_failed' in request.POST:#审核失败
                record = Apply.objects.get(user=object_id)
                if record.state in [ApplyState.WAIT_AUDIT,ApplyState.WAIT_REAUDIT]:
                    if record.audit_failed(request.user.id,request.POST.get('auditinfo',u'null')):
                        msg = u'管理员[%s]审核申请表[%s]失败'%(request.user.id,record.user)
                        OpLog.objects.log_action(request.user.id,1,u'审核失败',msg)
                        messages.info(request,u'审核成功')
                        return HttpResponseRedirect(u'/admin/%s/%s' % (Apply._meta.app_label.lower(),Apply.__name__.lower()))
                    else:
                        messages.error(request,u'写入审核失败信息失败')
                        return HttpResponseRedirect(u'/admin/%s/%s' % (Apply._meta.app_label.lower(),Apply.__name__.lower()))
                
                messages.error(request,u"只有等待审核或者等待复审的申请表可以审核失败！")
                return HttpResponseRedirect(u'/admin/%s/%s/%s/' % (Apply._meta.app_label.lower(),Apply.__name__.lower(),object_id))
        
        return super(type(self),self).change_view(request,object_id,extra_context)

    def get_readonly_fields(self,request,obj=None):
        if obj:
            return self.readonly_fields
        return ()

    def trade_setting(self,request):
        if request.method == 'POST':
            #pdb.set_trace()
            passedForm = ApplyPassForm(request.POST)
            uid_list = request.POST.get('queryset','').split(',')
            count = 0
            if passedForm.is_valid():
                _data = passedForm.cleaned_data
                for uid in uid_list:
                    try:uid = int(uid)
                    except:continue
                    proxy = UserProxy.objects.get(pk=uid)
                    proxy.set_trade_limit(_data['deposit_amount'],_data['credit_amount'])
                    proxy.bind_to_channel(_data['channel_name'],_data['mcc'])
                    proxy.set_amount_limit(_data['deposit_rate'],_data['credit_rate'],_data['fee_max'])
                    count = count + 1

                messages.info(request,u"审核%s个用户成功" % count)
                return HttpResponseRedirect('/admin/%s/%s'%(Apply._meta.app_label,Apply._meta.module_name)) 
            else:
                context = {
                    'queryset':[{'user':item} for item in uid_list],
                    'forms':passedForm,
                    'opts':Apply._meta,
                }
                return render_to_response('admin/audit/apply/apply_pass.html',context,context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect('/admin/')
     
    def get_urls(self):
        urls = super(type(self),self).get_urls()

        ext_url = patterns('',
            url(r'^passed/$',self.trade_setting,name='apply_passed_setting'),
        )
        return ext_url + urls;
 
class ApplyCodeAddForm(forms.ModelForm):
    code = forms.CharField(max_length=32, label=u'邀请码', required=False,help_text=u'为空则系统自动生成邀请码')
    
    def clean_code(self):
        code = self.data.get('code',None)
        if code is None or len(code) == 0:
            code = random.randint(10000000,99999999) 
            while ApplyCode.objects.filter(code=code).count() > 0:
                code = random.randint(10000000,99999999) 
        
        if ApplyCode.objects.filter(code=code).count() > 0:
            raise forms.ValidationError(u'此邀请码已经存在，请更换或者修改原邀请码！')
        msg = u'管理员[%s]添加邀请码[%s]'%(self.userid,code)
        OpLog.objects.log_action(self.userid,1,u'审核通过',msg)
        return code;
    
    class Meta:
        model = ApplyCode

class ApplyCodeForm(forms.ModelForm):
    class Meta:
        model = ApplyCode

class ApplyCodeAdmin(MisDBModelAdmin):
    list_display = ('code', 'used', 'city', 'src', 'usertype', 'mcc','terminalid')
    list_filter = ['src',]
    
    def applycode_import(self,request):
        error = None
        if request.method == 'POST':
            if 'csvfile' in request.FILES:
                try:
                    file = request.FILES['csvfile']
                    if os.path.splitext(file._name)[1].lower() != '.csv':
                        raise Exception(u'亲！文件扩展名错误，请上传csv文件！')
                    lines = csv_readlines(request.FILES.get('csvfile'))
                    wb = Workbook()
                    ws0 = wb.add_sheet('0')
                    col=0
                    field_names=['groupid','terminalid','applycode']
                    for field in field_names:
                            ws0.write(0,col,field)
                            col = col+1 
                    row = 1
                    for item in lines and lines or []:
                        #print item
                        if item and len(item) >= 2 and \
                            len(item[0]) == 5 and len(item[1]) == 20:
                            code = gen_applycode(item[1]) #item[3]
                            if ApplyCode.objects.filter(src=item[0],terminalid=item[1]).count() == 0:
                                ApplyCode.objects.create(code=code,
                                                         city='0000',
                                                         src=item[0],
                                                         usertype=item[2],
                                                         mcc='0000',
                                                         used=1,
                                                         terminalid=item[1])
                            else:
                                code = ''
                            ws0.write(row,0,item[0]);ws0.write(row,1,item[1]);ws0.write(row,2,code)
                            row = row+1
                            
                    xlsPath = u'/tmp/%s_aplcode_%s.xls' % (request.user.id,str(uuid.uuid1()).replace('-',''))
                    wb.save(xlsPath)
                    response = HttpResponse(open(xlsPath, 'r').read(), mimetype='application/ms-excel')
                    response['Content-Disposition'] = 'attachment; filename=applycode.xls'
                    return response 
                except Exception,ex:
                    error = ex.message
            else:
                error=u'请上传读卡器与渠道关系的csv文件'
        
        context = {
            'opts':ApplyCode._meta,
            'errorMsg': error
        }
        return render_to_response('admin/audit/applycode/applycode_import.html',context,context_instance=RequestContext(request))

    def get_urls(self):
        urls = super(type(self),self).get_urls()

        ext_url = patterns('',
            url(r'^import/$',self.applycode_import,name='applycode_import'),
        )
        return ext_url + urls;

        

    def get_form(self,request,obj=None,**kwargs):
        if obj is None:
            self.form = ApplyCodeAddForm
        else:
            self.form = ApplyCodeForm
        setattr(self.form, 'userid',request.user.id)
        return super(type(self),self).get_form(request,obj,**kwargs)

class VerifyCodeAdmin(MisDBModelAdmin):
    list_display = ('mobile', 'email', 'code', 'flag','created')
    date_hierarchy='created'
    
    def manual_send(self,request):
        if not request.user.is_superuser:
            return HttpResponseRedirect('/admin')
        errorMsg = None
        if request.method == 'POST':
            mobile_list,content = request.POST.get('mobile_list',''),request.POST.get('sms_content',u'测试短信网关')
            _log.info(u'mobile:%s|content:%s' % (mobile_list,content))
            
            result = []
            for mobile in [m for m in mobile_list.split(',') if m.isdigit() and len(m) == 11]:
                result.append(mobile)
                sendsmsv2(mobile,content)

            errorMsg = ','.join(result)
        
        return render_to_response('admin/audit/verifycode/manual_send_sms.html',
            {'opts':VerifyCode._meta,
             'errorMsg':errorMsg},
            context_instance = RequestContext(request))

    def get_urls(self):
        urls = super(type(self),self).get_urls()

        ext_url = patterns('',
            url(r'^manual_send/$',self.manual_send,name='manual_send_code'),
        )
        
        return ext_url + urls;

class UpgradeAdmin(MisDBModelAdmin):
    list_display = ('id','user_id','original_level','apply_level','state','memo')
class AuditLogAdmin(MisDBModelAdmin):
    search_fields = ['user_id']
    list_display = ('id','ext_key','user_id','type','apply_level','groupid','result','memo')
    date_hierarchy='create_date'

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

admin.site.register(Apply, ApplyAdmin)
admin.site.register(ApplyCode, ApplyCodeAdmin)
admin.site.register(VerifyCode, VerifyCodeAdmin)
admin.site.register(Upgrade,UpgradeAdmin)
admin.site.register(AuditLog,AuditLogAdmin)
admin.site.register(OpLog,OpLogAdmin)

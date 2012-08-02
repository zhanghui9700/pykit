#!/usr/bin/env python
# -*- coding=utf-8 -*-

import pdb,datetime,logging

from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator,InvalidPage,EmptyPage
from django.db.models import Count

from audit.models import VoucherConfirmInfo 
from audit.models import Upgrade as _up,AuditLog,UpgradeVoucher
from core.models import Person as _p,SPerson as _sp,Merchant as _m,PersonProxy,SPersonProxy,MerchantProxy,UserProxy
from util.define import UPGRADE_STATE,UserType,AccountType,UPGRADE_IMAGE,LICENSE_TYPE,UPGRADE_SOURCE
from util.common import PageList

TEMPLATE_PATH = {'AUTO_RESULT':'mis/audit_result.html',
                 'MANUAL_AUDIT':'mis/audit_voucher_confirm_v2.html'
                }

_logerror = logging.getLogger('mis_error')
_loginfo = logging.getLogger('mis_info')

def get_audit_result(upgradeState):
    audit_result = []
    try:
        uplist = _up.objects.filter(state=upgradeState).order_by('submit_time')
        for up in [c for c in uplist and uplist or []]:
            user = UserProxy.objects.get(pk=up.user_id)
            #pdb.set_trace()
            audit_result.append({'uid':user.id,
                                   'up_id':up.pk,
                                   'level':up.apply_level,
                                   'leveldesc':user.get_level_desc(up.apply_level),
                                   'up_source':UPGRADE_SOURCE.get_source_desc(up.up_source),
                                   'submittime':up.submit_time,
                                   'name':user.get_xuser().__dict__.get('username') or user.get_xuser().__dict__.get('company'),
                                   'type':user.user_type,
                                   'typedesc':user.get_type_desc()})
    except Exception,e:
        _logerror.error(e.message)
        
    return audit_result

def auto_result(request,page=1):
    '''
    #自动审核结果列表,暂时只显示升级失败
    #https://docs.djangoproject.com/en/1.3/topics/pagination/
    '''
    if request.method == 'GET' or request.method == 'POST':
        
        auto_audit_failure = get_audit_result(UPGRADE_STATE.AUTO_FAILURE)
        pager = Paginator(auto_audit_failure,10)
        try:
            auditResult = pager.page(page)
        except (EmptyPage,InvalidPage):
            page = pager.num_pages
            auditResult = pager.page(pager.num_pages)

        list_pages=PageList(pager.num_pages,page)

        return render_to_response(TEMPLATE_PATH.get('AUTO_RESULT') ,{'auditResult':auditResult,'pagenums':list_pages},context_instance=RequestContext(request))
    else:
        raise Http404('http get or post only!!')

def manual_audit(request,upid=0):
    '''
    自动审核失败的需要手动确认一下凭证信息是否正确
    '''
    if request.method == 'GET':
        #pdb.set_trace()
        qs = VoucherConfirmInfo.objects.filter(upgrade_id__id=upid,state=0)
        ConfirmList = {} #需要手动确认的字段列表，按照凭证类型分类
        for item in qs:
            ConfirmList.setdefault(LICENSE_TYPE.get_form_by_type(item.cert_type),[]).append(item)
        
        if len(ConfirmList) == 0:
            raise Http404(u'你要查询的数据不存在，请确认你所请求的页面是否正确！')
        

        voucherList = UpgradeVoucher.objects.filter(upgrade_id__id=upid)
        VoucherImage = {}
        for item in voucherList:
            VoucherImage.setdefault(LICENSE_TYPE.get_form_by_type(item.cert_type),[]).append(item)

        ConfirmList['licenseCounter']=len(ConfirmList)
        ConfirmList['upid'] = upid
        
        return render_to_response(TEMPLATE_PATH.get('MANUAL_AUDIT'),{'ConfirmList':ConfirmList,'VoucherImage':VoucherImage},context_instance=RequestContext(request))
    else:
        raise Http404('http get only!!')

def voucher_confirm(request):
    '''
    凭证手动确认的异步action
    把客户端手工确认回传回的信息更新到mis_voucher_confirminfo，然后把信息同步到person/sperson/merchant
    request.POST{
    IDCardInfoForm_id_number= 2_
    IDCardInfoForm_username = 3_张三
    __type    = IDCardInfoForm
    __typekey = 1
    __upid    = upgrade.id
    }
    '''
    if request.method == 'POST':
        #pdb.set_trace()
        #fieldValue = [('id_number':'2_'),('username':'3_张三')]
        fieldValue = [(key[len(request.POST.get('__type'))+1:],request.POST[key]) for key in request.POST.keys() if key.startswith(request.POST.get('__type'))]
        confirm = VoucherConfirm(currentUser = request.user,
                                  upid=request.POST.get('__upid'),
                                  cert_type=request.POST.get('__typekey'),
                                  fieldValue=fieldValue)

        if confirm.save_correct():
            return HttpResponse('{"statusCode":"200"}')
        else:
            return HttpResponse('{"statusCode":"500"}')

    else:
        raise Http404('http post only!')

def manual_submit(request):
    if request.method == "POST":
        upid,action = int(request.POST.get('__upid',0)),request.POST.get('__action')
        
        up = _up.objects.get(pk=upid)
        diffResult = {}
        #pdb.set_trace()
        if getattr(up,action)(request.user):
            for form in LICENSE_TYPE.LC_FORM:
                if len(form) > 0:
                    for key in request.POST.keys():
                        if key.startswith(form):
                            diffResult.setdefault(form,{})[key[len(form)+1:]] = request.POST.get(key)

        confirm = VoucherConfirm(currentUser=request.user,
                                 upid = up.id,
                                 diffResult = diffResult)
        if confirm.sync_to_core():
            return HttpResponse('{"statusCode":"200"}')
        else:
            return HttpResponse(u'{"statusCode":"500","msg":"%s"}' % confirm.errorMsg)

class VoucherConfirm:
    '''
    凭证手工验证类，审核用户录入信息和录入员录入信息的正确性，并对用户升级请求作出响应!
    '''
    def __init__(self,currentUser = None,upid=0,diffResult=None):
        self.currentUser = currentUser
        self.upgrade = _up.objects.get(pk=upid) 
        self.user = User.objects.get(pk=self.upgrade.user_id)
        self.diffResult = diffResult
        self.errorMsg = u''
        self.core_user = self.get_xuser()

    def get_xuser(self):
        '''
        获取一个用户的具体类型
        '''
        userGetter = {
            'USERTYPE_1':lambda uid : _p.objects.get(user__id=uid),
            'USERTYPE_2':lambda uid : _sp.objects.get(user__id=uid),
            'USERTYPE_3':lambda uid : _m.objects.get(user__id=uid)}
        
        return userGetter.get('USERTYPE_'+str(self.user.user_type))(int(self.user.id))
        
    def sync_to_core(self):
        '''
        1.把确认信息写入mis_voucher_confirminfo表
        2.修改UpgradeVoucher表的凭证审批字段
        3.把信息同步到具体的P/SP/M
        '''
        for license in self.diffResult:
            autoAuditFailureFields = VoucherConfirmInfo.objects.filter(upgrade_id=self.upgrade,cert_type=LICENSE_TYPE.LC_FORM.index(license))
            
            for field in autoAuditFailureFields:
                source,value = self.diffResult.get(license).get(field.field).split('_')
                print source,value
                if source ==  '1':value = field.input_value;
                elif source == '2':value = field.typist_value;

                field.state = 1
                field.create_user  = self.currentUser.id
                field.value_source = source
                field.confirm_value = value
                field.save()
                print license,field.field

            _loginfo.info(u'凭证人工审核-成功,upgrade_id:%s,cert_type:%s' % (self.upgrade.id,license))
        self._sync_to_xuser(fields=autoAuditFailureFields)

        return True

    def _sync_to_xuser(self,fields=None):
        '''
        同步确认信息到P/SP/M
        '''
        try:
            xuser = self.core_user 
            for item in fields:
                setattr(xuser,item.field,item.confirm_value)
            xuser.save()
        except Exception,e:
            _logerror.exception(e)

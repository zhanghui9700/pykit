#-*- coding=utf-8 -*-
import pdb

from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db.models import Q

from core.models import Recharge
from util.define import ApplyState,BuyType,GROUP_ID
from audit.models import Apply

def check_user_state():
    '''
    判断auth_user.state是否可以登录
    包含购买读卡器信息
    '''
    def decorate(view_func):
        def _wrapped_view(request, *args, **kwargs):
            ac = User.objects.get(id=request.user.id).state
            
            if ac < 2:                 #申请表待审核或者申请信息没完整[0,1]
                try:
                    apply = Apply.objects.get(user=request.user.id)
                    if int(apply.groupid) == GROUP_ID.Shenma:
                        return HttpResponseRedirect(reverse('shenma_profile_info'))
                except:pass 
                return HttpResponseRedirect(reverse('apply_profile_info'))
            if ac in [2,3]:          #审核通过的用户 [2]
                apply = Apply.objects.get(user=request.user.id)
                query = Q(userid = request.user.id) & (
                (Q(type=BuyType.BUY_DEPOSITE)&Q(status=1)) |
                Q(type=BuyType.BUY_COD) | Q(type=BuyType.SHENMA))
                charges = Recharge.objects.filter(query)
                if charges.count() == 0 \
                    and (apply.groupid == GROUP_ID.Qianfang):
                    return HttpResponseRedirect(reverse('apply_buy_terminal'))
            elif ac > 4:                #账户异常 [5...]
                    return HttpResponseRedirect('/blocked')

            return view_func(request,*args,**kwargs)
        return _wrapped_view

    return decorate

def check_apply_state(allow_state_list=None):
    '''
    注册流程申请状态检查
    检查Apply.State
    根据不同的state导向到不同的注册页面
    避免用户注入，跨过流程
    '''
    allow_state_list = allow_state_list or []
    def decorate(view_func):
        def _wrapped_view(request, *args, **kwargs):
            try:
                apply = Apply.objects.get(user=request.user.id)
            except:
                user = request.user
                apply = Apply.objects.create(user=user.id,
                                             mobile=user.username,
                                             usertype=user.user_type,
                                             state=ApplyState.REGISTERED)
            if apply.state in allow_state_list:
                if apply.state == ApplyState.PASSED:
                    query = Q(userid = request.user.id) & (
                    (Q(type=BuyType.BUY_DEPOSITE)&Q(status=1)) |
                    Q(type=BuyType.BUY_COD)|Q(type=BuyType.SHENMA)) 

                    if Recharge.objects.filter(query).count() > 0 \
                        or apply.groupid != GROUP_ID.Qianfang:
                        return HttpResponseRedirect(reverse('account_info'))

                return view_func(request,*args,**kwargs)
            else:
                return HttpResponseRedirect(get_url_by_apply_state(apply))
        
        return _wrapped_view
    return decorate

APPLY_STATE_URL = {
    'STATE_0':'apply_profile_info', #已注册        -》基本信息
    'STATE_1':'apply_upload_file',  #已填写基本信息-》上传附件
    'STATE_2':'apply_wait_audit',   #上传附件      -》等待审核
    'STATE_3':'apply_wait_audit',   #暂时没有state = 3
    'STATE_4':'apply_wait_audit',   #等待审核      -》审核提示
    'STATE_5':'apply_buy_terminal', #通过          -》购买读卡器 or account
    'STATE_6':'apply_wait_audit',   #失败          -》审核提示
    'STATE_7':'apply_wait_audit',   #失败          -》审核提示
    'STATE_8':'apply_wait_audit',   #复审          -》审核提示
}
SHENMA_APPLY_STATE_URL = {
    'STATE_0':'shenma_profile_info', #已注册        -》基本信息
    'STATE_1':'shenma_upload_file',  #已填写基本信息-》上传附件
    'STATE_2':'shenma_wait_audit',   #上传附件      -》等待审核
    'STATE_3':'shenma_wait_audit',   #暂时没有state = 3
    'STATE_4':'shenma_wait_audit',   #等待审核      -》审核提示
    'STATE_5':'shenma_buy_terminal', #通过          -》购买读卡器 or account
    'STATE_6':'shenma_wait_audit',   #失败          -》审核提示
    'STATE_7':'shenma_wait_audit',   #失败          -》审核提示
    'STATE_8':'shenma_wait_audit',   #复审          -》审核提示
}

def get_url_by_apply_state(apply=None):
    if apply is None or apply.state not in ApplyState.keys():
        return reverse('apply_basic_info')
    else:
                
        if apply.groupid == GROUP_ID.Shenma:
            urlName = SHENMA_APPLY_STATE_URL.get(u'STATE_%s' % apply.state,'shenma_basic_info') 
        else:
            urlName = APPLY_STATE_URL.get(u'STATE_%s' % apply.state,'apply_basic_info')
        
        try:
            return reverse(urlName)
        except:
            return '/signup'

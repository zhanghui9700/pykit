# Create your views here.
#coding=utf-8
import json
import alipay
import datetime
import pdb
import re
import sys,logging,qfpay

from functools import wraps
from django.utils.decorators import available_attrs
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.utils.decorators import available_attrs
from django import forms
from django.db.models import Q

from util.decorator import check_apply_state
from forms import UserForm, SMSPersonForm, LoginForm, SMPersonForm, SMCompanyForm,ShenmaUserForm
from models import Apply, ApplyCode, VerifyCode
from core.models import Person,Recharge
from trade.models import Record
from audit.models import ControlTable,UpgradeProxy
from util.define import BuyType,UPGRADE_STATE,UPGRADE_SOURCE,ApplyState
from audit.models import Upgrade,UpgradeProxy
from util.city import citylist

from django.core.urlresolvers import reverse
#def reverse(urlname):
#    import django
#    return django.core.urlresolvers.reverse(urlname,urlconf='audit.shenma_urls')

nmlogging = logging.getLogger('normallog')

MODIFY_PWD_PREFIX = '修改密码所需验证码为：'
RESET_PWD_PREFIX = '重置密码的验证码为：'
GET_VERIFYCODE_PREFIX="欢迎注册钱方科技，您的验证码是"
MSG_END = '，该验证码5分钟内有效且只能输入一次，请勿泄露或转发。'

def check_normal_user():
    def __func__(view_func):
        def __wrapped_view(request, *args, **kwargs):
            if request.user.state==4:
                return render_to_response('msg/signup_not_allowed.html');
            return view_func(request, *args, **kwargs)
        return __wrapped_view
    return __func__

def check_register_state():
    '''
    检查Apply.State
    '''
    def decorate(view_func):
        def _wrapped_view(request, *args, **kwargs):
            applies = Apply.objects.filter(user=request.user.id)
            if applies.count()<=0:
                return HttpResponseRedirect(reverse('apply_basic_info'))
            register_state = applies[0].state
            if register_state==0:
                return HttpResponseRedirect(reverse('apply_profile_info'))
            elif register_state in range(1,4):
                return HttpResponseRedirect(reverse('apply_wait_audit'))
            return view_func(request,*args,**kwargs)
        return _wrapped_view

    return decorate

def sendmobilecode(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        type = request.POST.get('type')
        pattern = '^0{0,1}(13[0-9]|15[0-9]|18[6-9]|180)[0-9]{8}$'
        if not re.match(pattern, mobile):
            return HttpResponse(json.dumps({"ret": False, "msg": "无效手机号，验证码发送失败"}))
        code = VerifyCode.objects.generate_code(mobile=mobile)
        from util.sendsms import sendsms

        if type == u'signup':
            msg = GET_VERIFYCODE_PREFIX
        elif type == u'modify':
            msg = MODIFY_PWD_PREFIX
        elif type == u'forget':
            msg = RESET_PWD_PREFIX
        else:
            return HttpResponse(json.dumps({"ret":False, "msg":u"未知的请求类型"}))
        msg = msg+code+MSG_END
        #pdb.set_trace()
        refile=sendsms(mobile,unicode(msg))
        if refile == '0#1':
            return HttpResponse(json.dumps({"ret": True, "msg": u"验证码已经发送!"}))
        else:
            return HttpResponse(json.dumps({"ret": False, "msg": refile}))

SIGNUP_TEMPLATE_PATH = 'userportal/signup/shenma' #注册模板文件夹
SIGNUP_TEMPLATE_NAME = 'signup_shenma.html' #注册首页filename(不同渠道首页不同)

def signup(request): 
    if request.method == 'GET':
        return render_to_response('%s/%s'%(SIGNUP_TEMPLATE_PATH,SIGNUP_TEMPLATE_NAME), {"userform": ShenmaUserForm()},context_instance=RequestContext(request))
    else:
        userform = ShenmaUserForm(request.POST)
        if userform.is_valid():
            user = userform.create_user(user_type=request.POST.get('user_type'))
             
            from django.contrib.auth import authenticate, login
            user = authenticate(username=user.username, password=userform.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect(reverse('shenma_profile_info'))
        else:
            return render_to_response('%s/%s'%(SIGNUP_TEMPLATE_PATH,SIGNUP_TEMPLATE_NAME), {"userform": userform}, context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_apply_state(allow_state_list=[ApplyState.REGISTERED])
def signup2(request):
    user = request.user 
    a = Apply.objects.get(user=user.id)
    u = User.objects.get(id=user.id)
    if user.user_type == 1:
        if request.method == 'GET':
            pe = SMPersonForm()
            pe['mobile'].field.initial = u.mobile
            return render_to_response('%s/signup_person.html' % SIGNUP_TEMPLATE_PATH, {'personform': pe},
                context_instance=RequestContext(request))
        else:
            personform = SMPersonForm(request.POST)
            #pdb.set_trace()
            if personform.is_valid():
                personform.save(a)
                return HttpResponseRedirect(reverse('shenma_upload_file'))
            else:
                return render_to_response('%s/signup_person.html'%SIGNUP_TEMPLATE_PATH, {'personform': personform},
                    context_instance=RequestContext(request))
    elif user.user_type == 2:
        if request.method == 'GET':
            pe = SMSPersonForm()
            pe['mobile'].field.initial = u.mobile
            return render_to_response('%s/signup_sperson.html'%SIGNUP_TEMPLATE_PATH, {'spersonform':pe},
                context_instance=RequestContext(request))
        else:
            spersonform = SMSPersonForm(request.POST)
            if spersonform.is_valid():
                spersonform.save(a)
                return HttpResponseRedirect(reverse('shenma_upload_file'))
            else:
                return render_to_response('%s/signup_sperson.html'%SIGNUP_TEMPLATE_PATH, {'spersonform': spersonform},context_instance=RequestContext(request))
    elif user.user_type == 3:
        if request.method == 'GET':
            pe = SMCompanyForm()
            pe['mobile'].field.initial = u.mobile
            return render_to_response('%s/signup_company.html'%SIGNUP_TEMPLATE_PATH, {'companyform': pe},
                context_instance=RequestContext(request))
        else:
            companyform = SMCompanyForm(request.POST)
            if companyform.is_valid():
                companyform.save(a)
                return HttpResponseRedirect(reverse('shenma_upload_file'))
            else:
                return render_to_response('%s/signup_company.html'%SIGNUP_TEMPLATE_PATH, {'companyform': companyform},context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/puzzled')

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_apply_state(allow_state_list=[ApplyState.COMMITINFO])
def signup3(request):
    '''
    上传凭证后state处于等待审核
    '''
    if request.method == 'POST':
        upProxy = UpgradeProxy()
        upList = Upgrade.objects.filter(user_id=request.user.id,up_source=UPGRADE_SOURCE.APPLY)
        #pdb.set_trace()
        if len(upList) == 0:
            upgrade = Upgrade(user_id=request.user.id,
                          original_level = request.user.user_level,
                          up_source = UPGRADE_SOURCE.APPLY,
                          apply_level = request.user.user_level,
                          need_typist = 1,
                          input_state = 0,
                          state = UPGRADE_STATE.APPLY)
            
            if upProxy.create_up(upgrade):
                apl = Apply.objects.get(user=request.user.id)
                apl.state=ApplyState.WAIT_AUDIT
                apl.save()
                return HttpResponseRedirect(reverse('shenma_wait_audit'))
        else:
            return HttpResponseRedirect(reverse('shenme_wait_audit'))
    elif request.method == 'GET':
        if '_jump_upload' in request.GET.keys():
            apl = Apply.objects.get(user=request.user.id)
            apl.state=ApplyState.WAIT_AUDIT
            apl.uploadtime = datetime.datetime.now()
            apl.save()
            return HttpResponseRedirect(reverse('shenma_wait_audit'))

    return render_to_response('%s/signup3.html'%SIGNUP_TEMPLATE_PATH,{},context_instance=RequestContext(request))
 
@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_apply_state(allow_state_list=[ApplyState.WAIT_AUDIT,ApplyState.AUTO_AUDIT_FAILURE,ApplyState.AUDIT_FAILURE,ApplyState.WAIT_REAUDIT])
def signup4(request):
    apl = Apply.objects.get(user=request.user.id)
    context = {'wait_audit':apl.state == ApplyState.WAIT_AUDIT}
    return render_to_response('%s/signup4.html'%SIGNUP_TEMPLATE_PATH,context,context_instance=RequestContext(request))
 
@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_apply_state(allow_state_list=[ApplyState.PASSED])
def signup5(request):
    user=request.user
    a=Apply.objects.get(user=user.id)
    if a.src == GROUP_ID.Shenma:
        return HttpResponseRedirect(reverse('shenma_apply_success'))
    
    address = a.businessaddr+' '+a.contact+' '+a.mobile
    if request.method == "GET":
        query = Q(userid = request.user.id) & (
            (Q(type=BuyType.BUY_DEPOSITE)&Q(status=1)) |
            Q(type=BuyType.BUY_COD))
        if Recharge.objects.filter(query).count() > 0:
            return HttpResponseRedirect('/account')
        else:
            return render_to_response('%s/signup5.html'%SIGNUP_TEMPLATE_PATH, {'address': address}, context_instance=RequestContext(request))
    else: #用户提交的付款表单
        post = request.POST
        num=0.0
        product_name = ''
        product_desc = ''
        buy_type = post['pay_deposit']
        pay_type = 0
        desc = ''
        use_old_addr = post['old_addr']
        
        if use_old_addr == 'old':
            desc =  address
        else:
            desc += citylist[int(post['province'])]['n']+citylist[int(post['province'])]['c'][int(post['city'])]
            desc += post['address']+';'
            #desc += post['post']+';'
            desc += post['contact']+';'
            desc += post['mobile']

        if buy_type == 'deposit':
            pay_type = BuyType.BUY_DEPOSITE
            product_name = u'押金'
            num = 200
        elif buy_type == 'cod':
            pay_type = BuyType.BUY_COD
            product_name = u'货到付款'
            num = 0
        else:
            return HttpResponse(json.dumps({'ret':False,'msg':'Unsupported type of purchasing!'}))
        product_desc = u'购买钱方科技的读卡器'
        
        if buy_type == 'cod':
            charges = Recharge.objects.filter(userid = request.user.id, type=BuyType.BUY_COD)
            if charges.count()<=0:
                charge = Recharge(userid=request.user.id, type=pay_type, fee=num, desc=desc, status=0)
                charge.save()
                return HttpResponseRedirect(reverse('apply_buy_success'))
                #return render_to_response('msg/paid_cod_success.html')
            else:
                return render_to_response('msg/paid_cod_not_allowed.html')
        charge = Recharge(userid=request.user.id, type=pay_type, fee=num, desc=desc, status=0)
        charge.save()

        
        pay = alipay.Alipay()
        num = 0.01
        return_url = qfpay.QF_DOMAIN+'/charge_return'
        notify_url = qfpay.QF_DOMAIN+'/charge_notify'
        url = pay.create_order_url(
            '2088002089455812',
            'create_direct_pay_by_user',
            'fenyon@126.com',
            '',
            return_url,notify_url,
            product_name,
            product_desc,
            charge.id, num)
        return HttpResponseRedirect(url)

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
#@check_apply_state(allow_state_list=[ApplyState.PASSED])
def signup6(request):
    return render_to_response('%s/signup6.html'%SIGNUP_TEMPLATE_PATH)

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_apply_state(allow_state_list=[ApplyState.PASSED])
def charge_notify(request):
    buyer = request.POST['buyer_email']
    buyerid = request.POST['buyer_id']
    fee = float(request.POST['total_fee'])
    no = request.POST['out_trade_no']
    trade_status = request.POST['trade_status']

    nmlogging.info('alipay notify: buyer:%s buyerid:%s trade_no:%s status:%s' %(buyer, buyerid, no, trade_status))
    if trade_status == 'TRADE_SUCCESS':
        charge = Recharge.objects.get(id = no) #付款成功
        charge.status = 1
        charge.sucesstime = datetime.datetime.now()
        charge.buyer = buyer
        charge.buyerid = buyerid
        if fee != charge.fee:
            nmlogging.error('Different pay number: tradeno:%s, orig:%f, now:%f' %(no, charge.fee, fee))
        charge.save()
    nmlogging.info('Pay seccess : trade_no:%s' %no)
    return HttpResponse('success')


@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_apply_state(allow_state_list=[ApplyState.PASSED])
def charge_return(request):
    issuc = request.GET['is_success']
    total = request.GET['total_fee']
    buyer = request.GET['buyer_email']
    seller = request.GET['seller_email']
    
    nmlogging.warning('Pay return: %s, %s, %s' %(issuc, total, buyer))
    if issuc == 'T':
        s = u'<div style="padding:10px;width:300px;border:1px solid #cccccc;">支付宝交易成功! 金额:' + `total` + u'</div>'
        return render_to_response('msg/paid_success.html', {},context_instance=RequestContext(request))
    else:
        s = u'<div style="padding:10px;width:300px;border:1px solid #cccccc;">支付宝交易失败!</div>'
        return HttpResponse(s)

def validate(request):
    if request.method == 'GET':
        return HttpResponse(json.dumps({'ret':False,'msg':'只支持POST请求'}))
    else:
        post = request.POST
        if post['type'] == 'mobile':
            mobile = post['mobile']
            users = User.objects.filter(mobile = mobile)
            if users.count()<=0:
                return HttpResponse(json.dumps({'ret':True,'msg':'正确的手机号'}))
            else:
                return HttpResponse(json.dumps({'ret':False,'msg':'已注册的手机号'}))
        elif post['type'] == 'verifycode':
            mobile,code= post['mobile'],post['code']
            pattern = '^[0-9]{6}$'
            if not re.match(pattern,code): 
                return HttpResponse(json.dumps({'ret':False, 'msg':'验证码为六位数字'}))
            codes = VerifyCode.objects.filter(mobile=mobile,code=code,flag=0)
            if codes.count()<=0:
                return HttpResponse(json.dumps({'ret':False,'msg':'错误的验证码'}))
            else:
                time_delta = datetime.datetime.now()-codes[0].created
                if time_delta>datetime.timedelta(minutes=5):
                    return HttpResponse(json.dumps({'ret':False,'msg':'过期的验证码'}))
                else:
                    return HttpResponse(json.dumps({'ret':True, 'msg':'正确的验证码'}))
        elif post['type'] == 'password':
            mobile,pwd = post['mobile'], post['password']
            users = User.objects.filter(mobile=mobile)
            if users.count()<=0:
                return HttpResponse(json({'ret':True,'msg':'错误的手机号'}))
            else:
                user = users[0]
                if user.check_password(pwd):
                    return HttpResponse(json.dumps({'ret':True,'msg':'原密码'}))
                else:
                    return HttpResponse(json.dumps({'ret':False,'msg':'非原密码'}))
        else:
            return HttpResponse(json.dumps({'ret':False,'msg':'不正确的验证类型'}))

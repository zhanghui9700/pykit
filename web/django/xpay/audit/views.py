# Create your views here.
#coding=utf-8
import json
import alipay
import datetime
import pdb
import re

from functools import wraps
from django.utils.decorators import available_attrs
from django.template import RequestContext
from django.http import HttpResponseRedirect, \
    HttpResponse, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.utils.decorators import available_attrs
from django.core.urlresolvers import reverse

from util.decorator import check_apply_state
from forms import UserForm, SPersonForm, LoginForm, PersonForm, CompanyForm
from models import Apply, ApplyCode, VerifyCode,AuditLog
from core.models import Person,Recharge,Invoice
from trade.models import Record
from django import forms
from django.db.models import Q
from audit.models import ControlTable,UpgradeProxy
import sys,logging,qfpay
from util.define import BuyType,UPGRADE_STATE,UPGRADE_SOURCE,ApplyState,UserType
from audit.models import Upgrade,UpgradeProxy
from util.city import citylist

reload(sys)
sys.setdefaultencoding('utf8')

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
        pattern = '^0{0,1}(13[0-9]|15[0-9]|18[0-9])[0-9]{8}$'
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
        refile = sendsms(mobile,unicode(msg))
        if refile == 'ok':
            return HttpResponse(json.dumps({"ret": True, "msg": u"验证码已经发送!"}))
        else:
            return HttpResponse(json.dumps({"ret": False, "msg": refile}))
            
SIGNUP_TEMPLATE_ROOT = 'userportal/signup/qfpay'

def signup(request,group=None):
    '''验证手机号，创建账号'''
    if request.user.is_authenticated():
        if request.user.state > 2:
            from django.contrib.auth import logout
            logout(request)
            return HttpResponseRedirect('/signin')
        else:
            return HttpResponseRedirect(reverse('apply_profile_info'))

    request.session['group'] = group
    userform = UserForm()
    if request.method == 'POST':
        userform = UserForm(request.POST)
        if userform.is_valid():
            user = userform.create_user() #todo:添加事务支持
            from django.contrib.auth import authenticate, login
            user = authenticate(username=user.username, \
                                password=userform.cleaned_data['password'])
            login(request, user)

            request.session['group'] = group
            return HttpResponseRedirect(reverse('apply_profile_info'))

    return render_to_response('%s/signup.html'%SIGNUP_TEMPLATE_ROOT, 
                                {"userform": userform},
                                context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_apply_state(allow_state_list=[ApplyState.REGISTERED])
def signup2(request):
    '''填写基本信息'''
    if request.user.user_type not in UserType.__dict__.values():
        raise Exception(u'用户类型错误,Uid:%s,Utype:%s'%(user.id,user.user_type))
    
    user,a = request.user,Apply.objects.get(user=request.user.id)  
    tmplt_path = ['',
                  '%s/signup_person.html'%SIGNUP_TEMPLATE_ROOT,
                  '%s/signup_sperson.html'%SIGNUP_TEMPLATE_ROOT,
                  '%s/signup_company.html'%SIGNUP_TEMPLATE_ROOT][request.user.user_type]
    tmplt_form = [{},
                  PersonForm,
                  SPersonForm,
                  CompanyForm][request.user.user_type]
    
    if request.method == 'POST':
        form = tmplt_form(request.POST)
        if form.is_valid():
            form.save(a)
            return HttpResponseRedirect(reverse('apply_upload_file'))
    else:
        form = tmplt_form()
        form["mobile"].field.initial = user.mobile
   
    context = [{},
              {'personform':form},
              {'spersonform':form},
              {'companyform':form}][request.user.user_type]
    
    return render_to_response(tmplt_path,
                              context,
                              context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_apply_state(allow_state_list=[ApplyState.COMMITINFO])
def signup3(request):
    '''上传凭证,然后state处于等待审核'''
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
                return HttpResponseRedirect(reverse('apply_wait_audit'))
        else:
            return HttpResponseRedirect(reverse('apply_wait_audit'))
    
    return render_to_response('%s/signup3.html'%SIGNUP_TEMPLATE_ROOT,
                              {},
                              context_instance=RequestContext(request))
 
@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_apply_state(allow_state_list=[ApplyState.WAIT_AUDIT,ApplyState.AUTO_AUDIT_FAILURE,ApplyState.AUDIT_FAILURE,ApplyState.WAIT_REAUDIT])
def signup4(request,group='qfpay'):
    apl = Apply.objects.get(user=request.user.id)
    apl.uploadtime = datetime.datetime.now()
    apl.save()
    context = {'wait_audit':apl.state == ApplyState.WAIT_AUDIT}
    return render_to_response('%s/signup4.html'%SIGNUP_TEMPLATE_ROOT,
                            context,
                            context_instance=RequestContext(request))

def create_invoice(request,buyername,buyercontactmethod,buyeraddress,buytype,num,count,au):
    '''创建发货单'''
    orderidindex = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    record = Invoice.objects.filter(orderid__contains=orderidindex).order_by('-id')
    
    last = '0001'
    if record.count()>0:
        last = int(record[0].orderid[14:])
        last += 1 
    orderid = orderidindex + str(last) 
    
    invo = Invoice(buyerid = request.user.id,
                    orderid = orderid,
                    orderformtype=2,
                    buyername=buyername,
                    buyercontactmethod=buyercontactmethod,
                    buyeraddress=buyeraddress,
                    buytype=buytype,
                    paymoney=num,
                    terminalcount = count,
                    paystate = 1,
                    former=au.create_user,
                    auditer=au.create_user,
                    producetime=au.create_date,
                    auditstate=2,
                    )
    invo.save()


@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_apply_state(allow_state_list=[ApplyState.PASSED])
def signup5(request):
    query = Q(userid = request.user.id) & (
            (Q(type=BuyType.BUY_DEPOSITE)&Q(status=1)) |
            Q(type=BuyType.BUY_COD))
        
    if Recharge.objects.filter(query).count() > 0:
        return HttpResponseRedirect('/account')

    user,a =request.user,Apply.objects.get(user=request.user.id)
    address = a.businessaddr+' '+a.contact+' '+a.mobile
    count = a.terminalcount
    everyterminalfee = 499
    fee = a.terminalcount * everyterminalfee
    
    if request.method == "GET":
        return render_to_response('%s/signup5.html'%SIGNUP_TEMPLATE_ROOT, 
                {'address': address,'fee':fee,'count':count}, 
                context_instance=RequestContext(request))
    else:
        post = request.POST
        num=0.0
        product_name = ''
        product_desc = ''
        buy_type = post['pay_deposit']
        pay_type = 0
        desc = ''
        use_old_addr = post['old_addr']
        
        buyername=''
        buyercontactmethod=''
        buyeraddress=''

        if use_old_addr == 'old':
            desc =  address 
            buyername=a.contact
            buyercontactmethod=a.mobile
            buyeraddress=a.businessaddr

        else:
            desc += citylist[int(post['province'])]['n']+citylist[int(post['province'])]['c'][int(post['city'])]
            desc += post['address']+';'
            desc += post['contact']+';'
            desc += post['mobile']

            buyername=post['contact']
            buyercontactmethod=post['mobile']
            buyeraddress=citylist[int(post['province'])]['n']+citylist[int(post['province'])]['c'][int(post['city'])]+post['address']

        if buy_type == 'deposit':
            pay_type = BuyType.BUY_DEPOSITE
            product_name = u'购买读卡器'
            num = a.terminalcount*everyterminalfee
        else:
            pay_type = BuyType.BUY_COD
            product_name = u'货到付款'
            num = a.terminalcount*everyterminalfee+20
        
        product_desc = u'购买钱方科技的读卡器'
       
        try:
            au = AuditLog.objects.filter(user_id = request.user.id,result=1).order_by("-id")[0]
        except:
            au = AuditLog(user_id=request.user.id,create_user=0,create_date=datetime.datetime.now())

        if buy_type == 'cod': #货到付款
            #创建购买记录和发货单              
            charge = Recharge(userid=request.user.id, type=pay_type, fee=num, desc=desc, status=0)
            charge.save()
            create_invoice(request,buyername,buyercontactmethod,buyeraddress,BuyType.BUY_COD,num,count,au)
            return HttpResponseRedirect(reverse('apply_buy_success'))
        else:
            #删除历史未付款单据 
            oldChanges = Recharge.objects.filter(userid = request.user.id,
                                                type=BuyType.BUY_DEPOSITE,
                                                status = 0)
            oldChanges.delete()

            charge = Recharge(userid=request.user.id, type=pay_type, fee=num, desc=desc, status=0)
            charge.save()
            create_invoice(request,buyername,buyercontactmethod,buyeraddress,BuyType.BUY_DEPOSITE,num,count,au)
            pay = alipay.Alipay()
            #num = 0.01
            return_url = qfpay.QF_DOMAIN+'/charge_return'
            notify_url = qfpay.QF_DOMAIN+'/charge_notify'
            url = pay.create_order_url(
                '2088002089455812', #partner
                'create_direct_pay_by_user',
                'fenyon@126.com',
                '',
                return_url,#pay succeed callback url
                notify_url, #???
                product_name,
                product_desc,
                charge.id, #钱方交易号
                num #price
                )
            nmlogging.info(url)
            return HttpResponseRedirect(url)

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
#@check_apply_state(allow_state_list=[ApplyState.PASSED])
def signup6(request):
    return render_to_response('%s/signup6.html'%SIGNUP_TEMPLATE_ROOT)

@check_apply_state(allow_state_list=[ApplyState.PASSED])
def charge_notify(request):
    '''付款成功异步回调url,接口级别的回调，只输出success'''
    buyer = request.POST['buyer_email']
    buyerid = request.POST['buyer_id']
    fee = float(request.POST['total_fee'])
    no = request.POST['out_trade_no']
    trade_status = request.POST['trade_status']

    nmlogging.info('alipay notify: buyer:%s buyerid:%s trade_no:%s status:%s' %(buyer, buyerid, no, trade_status))
    if trade_status == 'TRADE_SUCCESS': 
        try:
            charge = Recharge.objects.get(id = no) #付款成功
            charge.status = 1
            charge.sucesstime = datetime.datetime.now()
            charge.buyer = buyer
            charge.buyerid = buyerid


            if fee != charge.fee:
                nmlogging.error('Different pay number: tradeno:%s, orig:%f, now:%f' %(no, charge.fee, fee))
            charge.save()
        
            invo = Invoice.objects.get(buyerid = charge.userid)
            invo.paystate = 2
            invo.save()
        except Exception,ex:
            nmlogging.exception(ex)

    nmlogging.info('Pay seccess : trade_no:%s' %no)
    
    return HttpResponse('success')

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_apply_state(allow_state_list=[ApplyState.PASSED])
def charge_return(request):
    '''付款成功Alipay回调界面，一般显示付款成功信息'''
    #pdb.set_trace()
    issuc = request.GET.get('is_success','F')
    total = request.GET.get('total_fee','0')
    buyer = request.GET.get('buyer_email','0')
    seller = request.GET.get('seller_email','0')
    no = request.GET.get('out_trade_no','0')
    buyerid = request.GET.get('buyer_id','0')

    nmlogging.warning('Pay return: %s, %s, %s' %(issuc, total, buyer))
    if issuc == 'T':
        try:
            charge = Recharge.objects.get(id = no) #付款成功
            if charge.userid == buyerid:
                charge.status = 1
                charge.sucesstime = datetime.datetime.now()
                charge.buyer = buyer
                charge.buyerid = buyerid
                charge.save()
            else:
                raise Exception('charge no:%s,userid:%s,buyerid:%s'%(no,charge.userid,buyerid))
        except Exception,ex:
            nmlogging.exception(ex)

        s = u'<div style="padding:10px;width:300px;border:1px solid #cccccc;">支付宝交易成功! 金额:' + `total` + u'</div>'
        return render_to_response('msg/paid_success.html', {},context_instance=RequestContext(request))
    else:
        s = u'<div style="padding:10px;width:300px;border:1px solid #cccccc;">支付宝交易失败!</div>'
        return HttpResponse(s)

def signin(request):
    #userportal/signup/login_v2.html
    pdb.set_trace()
    _url = reverse('admin:audit:audit_apply_add')
    return render_to_response('userportal/signup/login_v2.html',{}, context_instance=RequestContext(request))


def blocked(request):
    return render_to_response('userportal/signup/signup_3_sorry.html', {}, context_instance=RequestContext(request))


def puzzled(request):
    return render_to_response('userportal/signup/puzzled.html', {}, context_instance=RequestContext(request))

def agreement(request):
    return render_to_response('userportal/agreement.html', {}, context_instance=RequestContext(request))

def privacy(request):
    return render_to_response('userportal/privacy.html', {}, context_instance=RequestContext(request))

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

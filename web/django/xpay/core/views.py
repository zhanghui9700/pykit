# Create your views here.
#coding=utf-8
import pdb
import datetime,time,os
import logging
from django.template import RequestContext
from django.http import HttpResponseRedirect, \
                        HttpResponse,HttpResponseForbidden,Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required 
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q,Sum,Count
from django.utils.translation import gettext_lazy as _
from django.core.urlresolvers import reverse

from audit.models import VerifyCode
from core.models import Person
from core.models import SPerson
from core.models import Merchant
from core.models import Recharge
from trade.models import Record, Channel
from core.forms import ModifyForm
from core.forms import ResetForm
from settle.models import Settle,Period
from qfpay import BILLS_LOCATION
import json
from util.define import PageSetting,BuyType
from util.decorator import check_user_state

nmlogger = logging.getLogger('normallog')
wflogger = logging.getLogger('wflog')

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_user_state()
def account(request):
    user = request.user
    user_type = request.user.user_type
    if user_type == 1:
        p=Person.objects.get(user=user)
    elif user_type == 2:
        p=SPerson.objects.get(user=user)
    elif user_type == 3:
        p=Merchant.objects.get(user=user)
    else:
        raise Exception('user_type is %s'%request.user.user_type)
    return render_to_response('userportal/accounts/info.html', {'p':p},context_instance=RequestContext(request))

TRADE_STATUS = {
    u'所有交易':0,
    u'交易成功':1,
    u'交易失败':2,
}

class TradeObj:    
    def __init__(self,record):
        self.orig = record
        self.trade_count = record.txamt/100.0
        if record.busicd == '201000':
            self.trade_count *= -1    
        
        if record.cardcd != None and record.cardcd != '':
            self.card_alter = record.cardcd[0:6]+"***"+record.cardcd[-4:]
            self.suffix_cardcd = record.cardcd[-6:]

def trans_records(records):
    results = []
    for record in records:
        results.append(TradeObj(record))
    return results

#list the trade record.
@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_user_state()
def tradelist(request):
    user = request.user
    date1,date2 = request.GET.get("t1",'').strip(' ').strip('\t'),request.GET.get("t2",'').strip(' ').strip('\t')
    status = request.GET.get("s",'').strip(' ').strip('\t')
    sn = request.GET.get("idx",'').strip(' ').strip('\t')
    card = request.GET.get("cd",'').strip(' ').strip('\t')
    try:
        money = int(float(request.GET.get("m"))*100.0)
    except:
        money = 0
    
    #查询所有交易流水表，获取到所有结果
    records = Record.objects.get_all_results(request.user.id,date1,date2,status,sn,card,money)
    nmlogger.info("user_id:%s,length:%s" %(request.user.id,len(records)))
    try:
       records_disp = trans_records(records)
    except:
        records_disp = []
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    from django.core.paginator import Paginator,Page

    pager = Paginator(records_disp, PageSetting.PageSize)
    try:
        show_page = pager.page(page)
    except:
        show_page = pager.page(pager.num_pages)
    
    from util.common import PageList
    list_pages=PageList(pager.num_pages,page)
    
    context = {
        'records':show_page,
        'date1':date1,
        'date2':date2,
        'card' :card,
        'status': status,
        'index': sn,
        'money' :money/100.0,
        'pagenums':list_pages

    }
    return render_to_response('userportal/accounts/search.html', context,context_instance=RequestContext(request))

#logout of the system, redirect to the login page
@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
def logout(request):
    from django.contrib.auth import logout
    logout(request)
   
    return HttpResponseRedirect('/signin')

# modify the user's password.    
@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_user_state()
def modifypwd(request):
    mobile = request.user.mobile
    if request.method == 'POST':
        modifypwdform = ModifyForm(request.POST)
        if modifypwdform.is_valid():
            data = modifypwdform.cleaned_data
            mobile = data['mobile']
            pwd = data['password']
            vc = data['verifycode']
            
            print mobile,pwd,vc
            try:
                code_instance = VerifyCode.objects.filter(mobile = mobile,code =vc, flag=0).order_by('-created')[0]
                code_instance.flag=1;
                code_instance.save()
                u = User.objects.get(id=request.user.id, mobile = mobile)
                u.set_password(pwd)
                u.save()
                from django.contrib.auth import authenticate,login
                user = authenticate(username=u.username,password=pwd)
                login(request,user)
                
                return render_to_response('msg/reset_success.html', {}, context_instance=RequestContext(request))
            except:
                nmlogger.error("error when modifying the password")
                return render_to_response('msg/system_error.html')
        else: 
            return render_to_response('userportal/accounts/modify_pwd.html',{'modifypwdform':modifypwdform}, context_instance=RequestContext(request))
    else:
        #get the reset-password page
        data = {
            'oldpassword':'', 'mobile':mobile, 'verifycode':'', 
            'password':'','repassword':''
        }
        form = ModifyForm(data=data,auto_id='id_%s')
        form.errors.clear()
        return render_to_response('userportal/accounts/modify_pwd.html', {'modifypwdform': form},context_instance=RequestContext(request))

def resetpwd(request):
    if request.method == 'POST':
        resetpwdform = ResetForm(request.POST)
        if resetpwdform.is_valid():
            data = resetpwdform.cleaned_data
            mobile = data['mobile']
            pwd = data['password']
            vc = data['verifycode']

            print mobile,pwd,vc
            try:
                codes = VerifyCode.objects.filter(mobile = mobile,code =vc, flag=0).order_by('-created')
                code_instance = codes[0]
                code_instance.flag=1;
                code_instance.save()
                u = User.objects.get(mobile = mobile)
                u.set_password(pwd)
                u.save()
                return HttpResponseRedirect('/signin')
            except:
                return HttpResponseRedirect('/resetpwd')
        else:
            return render_to_response('userportal/accounts/forget_pwd.html',{'resetpwdform':resetpwdform}, context_instance=RequestContext(request))

    else:
        #get the reset-password page
        return render_to_response('userportal/accounts/forget_pwd.html', {'resetpwdform': ResetForm()},context_instance=RequestContext(request))

def trans_settle(settles):
    for settle in settles:
        total_fee = settle.payfee+settle.qffee+settle.chnlfee
        setattr(settle,'fee',total_fee)
    return settles

class QFObject(object):
    pass

def get_month_settle(settles):
    now_date = datetime.datetime.now().date()
    month_start = datetime.date(year=now_date.year,month=now_date.month,day=1)
    pids = Period.objects.filter(start__year=now_date.year,start__month=now_date.month)
    month_settles = settles.filter(pid__in=pids)
    qs = settles.aggregate(tradesum=Sum('tradesum'),settlesum=Sum('settlesum'),settlecnt=Sum('settlecnt'), payfee=Sum('payfee'),
        qffee=Sum('qffee'),chnlfee=Sum('chnlfee'))

    try:
        fee = qs.get('payfee',0)+qs.get('qffee',0)+qs.get('chnlfee',0)
        tradesum = qs['tradesum']
        settlecnt = qs['settlecnt']
        settlesum = qs['settlesum']
    except:
        fee, tradesum, settlecnt,settlesum = 0,0,0,0
        
    month = QFObject()
    setattr(month, 'fee', fee)
    setattr(month, 'tradesum', tradesum)
    setattr(month, 'settlecnt', settlecnt)
    setattr(month, 'settlesum', settlesum)
    setattr(month, 'start', month_start)
    setattr(month, 'end' , now_date)

    return month

#查询商户资金报告
@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_user_state()
def report(request):
    start_date = request.GET.get('s', '')
    end_date = request.GET.get('e','')
    userid = request.user.id
    user_results = Settle.objects.filter(userid=userid).order_by('-pid')
    last_account = None
    if len(user_results)>0:
        last_account =user_results[0]
    month = get_month_settle(user_results)
    if start_date!='' and end_date!='':
        sdate = datetime.datetime.strptime(start_date,'%Y-%m-%d').date()
        edate = datetime.datetime.strptime(end_date,'%Y-%m-%d').date()
        results = []
        for res in user_results:
            if sdate<=res.pid.start and res.pid.end<=edate:
                results.append(res)
    else:
        results = user_results

    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    from django.core.paginator import Paginator,Page
    
    trans_settle(results)
    pager = Paginator(results, PageSetting.PageSize)
    try:
        show_page = pager.page(page)
    except:
        show_page = pager.page(pager.num_pages)
    
    from util.common import PageList
    list_pages=PageList(pager.num_pages,page)
    
    context = {
        'start' :start_date,
        'end'   :end_date,
        'last_account' : last_account,
        'month':month,
        'settles':show_page,
        'pages':list_pages
    }
    return render_to_response('userportal/accounts/report.html', context,context_instance=RequestContext(request))

#下载商户对账单
@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_user_state()
def dlbill(request):
    if request.method=='POST':
        return HttpResponse(json.dumps({'ret':False,'msg':'Can not accept the POST request.'}))
    from django.core.servers.basehttp import FileWrapper
    import mimetypes

    bill_date = request.GET['date']
    try:
        datetime.datetime.strptime(bill_date,'%Y%m%d')
    except:
        raise Http404
    userid = int(request.user.id)
    filename = BILLS_LOCATION+`userid`+'/'+bill_date+'.xls'
    try:
        wrapper = FileWrapper(open(filename))
        content_type = mimetypes.guess_type(filename)[0]
    except:
        raise Http404
    response = HttpResponse(wrapper, content_type=content_type)
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename=%d_%s.xls' %(userid,bill_date)
    return response

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
@check_user_state()
def tradedetail(request):
    user = request.user

    if request.method == 'GET':
        tradeid = request.GET.get('id')
        try:
            record = Record.objects.get_by_syssn(userid = user.id, sn=tradeid)
            record_obj = TradeObj(record)
            return render_to_response('userportal/accounts/receipt.html',{'record':record_obj}, context_instance=RequestContext(request))
        except:
            return HttpResponse(json.dumps({"ret":False,"msg":"无法查找到指定的数据!"}))
    else:
        return HttpResponse(json.dumps({"ret":False}))

def show_template(request):
    relpath = request.GET.get("path",None)
    if relpath:
        return render_to_response(relpath)
    else:
        raise Http404

TRADE_BUSICD = {'000000': u'消费', '200000': u'退货', '201000': u'撤销'}

def sign(request,sid):
    
    cardno = request.GET.get('cardno')
    if cardno:
        r = Record.objects.get_by_syssn('',sid,include_cancel=True)
        if r is None:
            return render_to_response('userportal/sign/sign.html',{'err':True}, context_instance=RequestContext(request))
        
        u = User.objects.get(id=r.userid)
        
        if u.user_type == 1: # 个人
            info = Person.objects.filter(user=r.userid)[0]
        elif u.user_type == 2: # 个体户
            info = SPerson.objects.filter(user=r.userid)[0]
            info.username = info.company
        else: # 商户
            info = Merchant.objects.filter(user=r.userid)[0]
            info.username = info.company

        showname = info.nickname or info.username
        
        ch = Channel.objects.get(code=r.chnlid)
        if ch.mchntid == r.chnluserid: # 钱方商户
            r.person = showname
            r.mchnt = r.chnlusernm
        else: # 通联商户
            r.person = '' # 无收款方
            r.mchnt = showname

        r.txamt_str = '%.2f' % (int(r.txamt)/100.0)
        r.cardcd_str = r.cardcd[:6] + '*'*(len(r.cardcd)-10) + r.cardcd[-4:]
        r.cardexpire_str = '20' + r.cardexpire[2:] + '/' + r.cardexpire[:2]
        r.busicd_str = TRADE_BUSICD[r.busicd]
        r.sysdtm_str = str(r.sysdtm)
        #if r.mchnt:
        #    r.mchnt_str = u'收款方:' + r.mchnt

        if r.cardcd[-6:] == cardno:
            return render_to_response('userportal/sign/index.html',{'record':r}, context_instance=RequestContext(request))
        else:
            return render_to_response('userportal/sign/sign.html',{'err':True}, context_instance=RequestContext(request))
    else:
        return render_to_response('userportal/sign/sign.html',{}, context_instance=RequestContext(request))



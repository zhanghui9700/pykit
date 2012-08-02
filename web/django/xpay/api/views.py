# Create your views here.
#coding=utf-8
from django.http import HttpResponseRedirect, \
    HttpResponse, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.decorators import available_attrs
from audit.models import Apply,UpgradeVoucher
from mis.models import Terminal,Psam
from core.models import TerminalBind
from qfpay import IP_LIST 
from util.define import TerminalUsedState,TerminalState,UserState
from util.imgstore import save_image,format_filename
from util.define import AccountState,AuditState,LICENSE_TYPE
import pdb,json,datetime,time,types

import logging

USER_TYPE = {
    'person':1,
    'sperson':2,
    'company':3
}

nmlogger = logging.getLogger('api_log')

public_required={'type':'string','provision':'string','province':'string','city':'string','businessaddr':'string','terminalcount':'int',\
    'mobile':'string','src':'string','bankname':'string','banktype':'int','bankuser':'string','bankaccount':'string','nickname':'string',\
    'idnumber':'string','idphoto1':'file','idphoto2':'file','idenddate':'date','debitfee':'float','creditfee':'float','debitlimit':'float',\
    'creditlimit':'float','allowarea':'string','business_attestphoto1':'file'}
public_optional={'post':'string','telephone':'string','email':'string','area':'string','contact':'string','business_attestphoto2':'file','business_attestphoto3':'file','business_attestphoto4':'file','business_attestphoto5':'file','business_attestphoto6':'file',
    'business_attestphoto7':'file','tid':'string','logisticaddr':'string','groupid':'int'}

cert_type = {'requirement':'gathering_attest','photo1':'photo1','photo2':'photo2','photo3':'photo3',
    'photo4':'photo4','licensephoto1':'license_page1','licensephoto2':'license_page2','idphoto1':'id_front','idphoto2':'id_back','leasephoto1':'contract','leasephoto2':'contract2','leasephoto3':'contract3','taxphoto':'payed_tax',
    'authidphoto1':'legal_person_auth_front','apply_num_photo':'apply_number','authidphoto2':'legal_person_auth_back','authagreement':'legal_person_auth','cardphoto':'user_bank_card',\
    'orgphoto':'org_code','business_attestphoto1':'business_attest_front','business_attestphoto2':'business_attest_other2','business_attestphoto3':'business_attest_other3',\
    'business_attestphoto4':'business_attest_other4','business_attestphoto5':'business_attest_other5','business_attestphoto6':'business_attest_other6',\
    'business_attestphoto7':'business_attest_other7','open_licensephoto':'open_license'}

def check_ip(func):
    def _func(*args, **kwargs):
        request = args[0]
        ip = request.META['REMOTE_ADDR']
        nmlogger.info(request.META)
        if ip not in IP_LIST:
            return HttpResponse(json.dumps({'ret':False,'msg':'Unrecognized IP address'}))

        return func(*args, **kwargs)
    return _func

def get_value(type, orig_value):
    if orig_value == None:
        return None
    if type=='string':
        if isinstance(orig_value, unicode):
            value = orig_value.encode('utf-8')
        else:
            value = str(orig_value)
    elif type == 'int':
        value = int(orig_value)
    elif type == 'float':
        value = float(orig_value)
    elif type == 'date':
        value = datetime.datetime(*time.strptime(orig_value,'%Y-%m-%d')[:3]).date()
    elif type == 'file':
        value = orig_value
    else:
        value = None
    return value

def set_attributes(user, apply, request, options):
    post = request.POST
    files= request.FILES
    for field,type in options.items():
        if field not in post and field not in files:
            continue
        if type == 'file':
            if files.get(field) != None:
                value = format_filename(files.get(field).name, field)[0]
                value = get_value(type,value)
        else:
            value = get_value(type,post.get(field))
            if value==None: continue
        setattr(apply,field, value)
        if type == 'file' and files.get(field)!=None:
            img_name = cert_type.get(field, 'other_voucher')
            img_type = LICENSE_TYPE.IMAGE_TYPE.get(img_name)
            save_image(int(user.id), img_name, request.FILES[field])
            cert_obj = UpgradeVoucher.objects.create(user_id=user.id, cert_type=img_type, name=img_name+'.jpg')
            cert_obj.save()

def get_apply_obj(user, request, required_fields, optional_fields):
    apply = Apply(user=user)
    
    set_attributes(user, apply, request, public_required)
    set_attributes(user, apply, request, required_fields)
    set_attributes(user, apply, request, public_optional)
    set_attributes(user, apply, request, optional_fields)

    apply.uploadtime = datetime.datetime.now()
    apply.usertype,apply.state = user.user_type,4
    return apply

#注册用户
def register_user(post):
    mobile = post['mobile']
    users = User.objects.filter(mobile = mobile)
    
    if users.count() >= 1:
        raise Exception('Has registered')
    else:
        username, email =  mobile, post.get('email',mobile)
        user_type = USER_TYPE.get(post['type'])
        now = datetime.datetime.now()
        user = User(username = username,  mobile=mobile,email = u'%s@qfpay.com' % mobile, user_type = user_type, state=1,\
            is_staff=False, is_active=False, is_superuser=False,last_login=now, date_joined=now )
        user.set_password('123456')
        user.save()
    return user
#检查各个字段的完备性
def check_fields(required_fields, request):
    post = request.POST
    files = request.FILES
    for field,type in required_fields.items():
        if type == 'file':
            if files.get(field) == None:
                return field + ' field is required!'
        else:
            if post.get(field) == None or len(post.get(field))==0:
                return field + ' field is required!'
    return ''


#注册个人用户
def register_person(request):
    required_fields = {'name':'string','requirement':'file','leasephoto1':'file'}
    optional_fields = {'cardphoto':'file','leasephoto2':'file','leasephoto3':'file'}
    
    post = request.POST
    msg = check_fields(public_required, request)
    if msg !='':
        return msg,None
    msg = check_fields(required_fields, request)
    if msg != '':
        return msg,None
    user = register_user(post)
    if user==None:
        return 'Has registered!',None
    apply = get_apply_obj(user, request,required_fields,optional_fields)
    apply.save()    

    return '',user

    #注册个体户
def register_sperson(request):
    required_fields = {'needauth':'int','legalperson':'string','licensenumber':'string','address':'string','licenseend_date':'date','licensephoto1':'file','leasephoto1':'file','requirement':'file'}
    optional_fields = {'name':'string', 'taxnumber':'string', 'taxphoto':'file','taxenddate':'date','authidphoto1':'file','authidphoto2':'file','authagreement':'file','cardphoto':'file','apply_num_photo':'file','leasephoto2':'file','leasephoto3':'file','licensephoto2':'file','orgphoto':'file'}

    post = request.POST
    msg = check_fields(public_required, request)
    if msg != '':
        return msg,None

    msg = check_fields(required_fields, request)
    if msg != '':
        return msg,None
    user = register_user(post)
    if user==None:
        return 'Has registered!',None

    apply = get_apply_obj(user, request, required_fields, optional_fields)
    apply.save()
    return '', user

#注册公司
def register_company(request):
    required_fields = {'needauth':'int','name':'string','legalperson':'string','address':'string','licensenumber':'string','licensephoto1':'file','licenseend_date':'date',
        'passcheck':'int','leasephoto1':'file'}
    optional_fields = {'founddate':'date', 'taxnumber':'string', 'taxphoto':'file','taxenddate':'date', 'authidphoto1':'file', 'authidphoto2':'file', 'authagreement':'file',
        'orgcode':'string','orgphoto':'file','requirement':'file','apply_num_photo':'file','leasephoto2':'file','leasephoto3':'file','licensephoto2':'file','open_licensephoto':'file'}
    post = request.POST
    msg = check_fields(public_required, request)
    if msg != '':
        return msg,None

    msg = check_fields(required_fields, request)
    if msg != '':
        return msg,None
    user = register_user(post)
    if user==None:
        return 'Has registered!',None
    apply = get_apply_obj(user, request, required_fields, optional_fields)
    apply.save()
    return '', user
#检查手机号是否已经注册过
def check_mobile(post):
    mobile = post['mobile']

    if mobile==None:
        return 'The request must contain the mobile field.'
    users = User.objects.filter(mobile = mobile)
    if users.count() >= 1:
        return 'The mobile has been registered.'
    return ''

#注册用户的入口
@check_ip
def signup(*args, **kwargs):
    request = args[0]
    post = request.POST
    
    user_type = request.POST.get('type')
    if user_type not in USER_TYPE:
        error_msg = json.dumps({'ret':'UNSUPORT_USER_TYPE','msg':'Unspported user type(person, sperson, company)'})
        response = HttpResponse(error_msg, mimetype="application/x-javascript")
        return response
    error_msg =  check_mobile(post)
    if error_msg != '':
        error_msg = json.dumps({'ret':'MOBILE_HAS_REGISTERED', 'msg':error_msg})
        return HttpResponse(error_msg, mimetype="application/x-javascript")
    try:
        error_msg,user = globals()['register_'+user_type](request)
    except Exception as e:
        User.objects.filter(mobile=post['mobile']).delete()
        return HttpResponse(json.dumps({'ret':'FAILED', 'msg':e.args}))
    if  error_msg == '':
        sign_state = json.dumps({'ret':'SUCCESS', 'msg':user.id})
    else:
        sign_state = json.dumps({'ret':'REQUIRED_FIELD_MISSING', 'msg':error_msg})
    return HttpResponse(sign_state,mimetype="application/x-javascript")

USER_STATE = {
    1:'USER_CREATE', 2:'USER_PASSED',3:'USER_ACTIVATE',4:'USER_NORMAL',5:'USER_ZOMBIE',
    6:'USER_BLOCKED', 7:'USER_DESTROY'}

APPLY_STATE = {
    0:'AUDIT_WAIT', 1:'AUDIT_WAIT', 4:'AUDIT_WAIT', 5:'AUDIT_PASSED', 6:'AUDIT_FAILURE',
    7:'AUDIT_REJECTED'
}
#查看用户状态
@check_ip
def status(*args, **kwargs):
    request = args[0]
    userid = args[1]
    
    users = User.objects.filter(id = userid)
    if users.count() <= 0:
        return HttpResponse(json.dumps({'ret':False, 'user_state':'Unregistered!','audit_state':'none'}))
    
    user = users[0]
    applies = Apply.objects.filter(user=user)
    if applies.count() <= 0:
        return HttpResponse(json.dumps({'ret':False, 'user_state':USER_STATE.get(user.state,'UNKNOWN'),\
        'audit_state':'No data'}))
    apply = applies[0]
    jsdata = json.dumps({'ret':True,'user_state':USER_STATE.get(user.state,'UNKNOWN'),\
            'audit_state':APPLY_STATE.get(apply.state, 'UNKNOWN')})

    return HttpResponse(jsdata,mimetype="application/x-javascript")

def bind(user, terms):
    for term in terms:
        psam = Psam.objects.filter(psamid=term.psamid)[0]
        bind = TerminalBind.objects.create(user=user,udid=user.username, terminalid=term.terminalid,psamid=psam.psamid,
            psamtp = psam.psamtp,tckkey=term.tck,pinkey1=psam.pinkey1,
            pinkey2=psam.pinkey2, mackey=psam.mackey,diskey=psam.diskey,
            fackey=u'%s%s'%(psam.producer,psam.model))
        if bind.pk > 0:
            term.user = user
            term.used = TerminalUsedState.AssignedUser
            term.save()
        bind.save()

    return True

#将指定的终端编号列表绑定到指定的商户
@check_ip
def termbind(*args, **kwargs):
    request = args[0]
    if request.method == 'GET':
        return HttpResponse(json.dumps({'ret':'METHOD_WRONG','msg':'This method does not support GET method'}))
    try:
        userid = int(request.POST['userid'])
        terms = request.POST['terms']
        chnl = int(request.POST['src'])
    except:
        return HttpResponse(json.dumps({'ret':'WRONG_PARAMS', 'msg':'Missing parameter'}))
    users = User.objects.filter(id=userid)
    if len(users) < 1:
        return HttpResponse(json.dumps({'ret':'USER_NOT_EXIST','msg':'The user does not exist'}))
    import string
    terminals = string.split(terms,';')
    all_terms = Terminal.objects.filter(terminalid__in=terminals, group_id=chnl, state=TerminalState.Normal) #used=TerminalUsedState.AssignedPasm
    if len(all_terms) != len(terminals):
        return HttpResponse(json.dumps({'ret':'WRONG_TERMID', 'msg':'Some of the terminals does not belong to you.'}))
    bind_state = TerminalBind.objects.filter(terminalid__in=terminals, state=2)
    if len(bind_state)>=1:
        return HttpResponse(json.dumps({'ret':'TERM_HAS_BINDED', 'msg':'The terminal has binded'}))
    
    bind(users[0], all_terms)
    return HttpResponse(json.dumps({'ret':'SUCCESS','msg':'Bind successed.'}))

@check_ip
def unbind(*args, **kwargs):
    request = args[0]
    if request.method == 'GET':
        return HttpResponse(json.dumps({'ret':'METHOD_WRONG','msg':'This method does not support GET method'}))
    userid = int(request.POST.get('userid'))
    term = request.POST.get('terminal')
    binds = TerminalBind.objects.filter(user=userid, terminalid = term, state=2)
    binds.delete()
    Terminal.objects.filter(terminalid=term).update(used=TerminalUsedState.AssignedPasm)
    return HttpResponse(json.dumps({'ret':'SUCCESS', 'msg':'Our system has cancel the bind relationship'}))

@check_ip
def bindstate(*args, **kwargs):
    request = args[0]
    if request.method == 'POST':
        return HttpResponse(json.dumps({'ret':'GET_METHOD_SUPPORT','msg':'The interface only accept the get method'}))
    userid = int(request.GET.get('userid'))
    binds = TerminalBind.objects.filter(user=userid,state=2)
    terms = []
    for bind in binds:
        terms.append(bind.terminalid)
    return HttpResponse(json.dumps({'ret':'SUCCESS','terms':repr(terms)}))


#补充额外信息
@check_ip
def addinfo(*args, **kwargs):
    request = args[0]
    post = request.POST
    try:
        userid=int(post['userid'])
        chnl = post['chnl']
        field_str = post['fields']
    except:
        return HttpResponse(json.dumps({'ret':'WRONG_PARAM','msg':'Wrong parameters'}))
    applies = Apply.objects.filter(user=int(userid), src=chnl)
    if len(applies) < 1:
        return HttpResponse(json.dumps({'ret':'USER_NOT_EXIST','msg':'The user does not exist!'}))
    apply = applies[0]
    import string
    fields = string.split(field_str,';')
    for field in fields:
        if field in request.POST:
            val = request.POST[field]
            setattr(apply, field, val)
            continue
        if field in request.FILES:
            file = request.FILES[field]
            img_name = cert_type.get(field, 'other_voucher')
            img_type = LICENSE_TYPE.IMAGE_TYPE.get(img_name)
            save_image(userid, img_name, file)
            cert_obj = UpgradeVoucher.objects.create(user_id=userid, cert_type=img_type, name=img_name+'.jpg')
            cert_obj.save()

            continue
    apply.save()
    return HttpResponse(json.dumps({'ret':'SUCCESS', 'msg':'We has reset the value of the specified field'}))

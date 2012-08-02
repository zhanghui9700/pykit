#coding=utf-8
import pdb,json,logging
from django.conf import settings
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.generic import FormView
from django.core.urlresolvers import reverse
from django.template import RequestContext

from mis.forms import LoginForm,IDCardInfoForm,TaxInfoForm,ContractInfoForm,OrgcodeInfoForm,LicenseInfoForm
from audit.models import Upgrade as _up,UpgradeProxy as _upProxy,UpgradeVoucher as _upVoucher,UpgradeVoucher as _upVoucherProxy

from util.define import LICENSE_TYPE,UPGRADE_STATE 

TEMPLATE_PATH = {'MIS_LOGIN':'mis/login.html',
                 'MIS_INDEX':'mis/typist_input.html',
                 'MIS_TYPIST_INPUT':'mis/typist_input.html',
                }

_logerror = logging.getLogger('mis_error')
_loginfo = logging.getLogger('mis_info')

def getTemplate(path):
    return TEMPLATE_PATH.get(path,'mis/login.html')

def index(request):
    return HttpResponseRedirect(reverse('mis_typist_list'))  #render_to_response(getTemplate('MIS_TYPIST_INPUT'),{},context_instance=RequestContext(request))

def login(request):
    if request.method == 'POST':
        return login_doPost(request)
    else:
        return login_doGet(request)

def login_doGet(request):
    return render_to_response(getTemplate('MIS_LOGIN'));

def login_doPost(request):
    loginForm = LoginForm(request.POST)
    if loginForm.is_valid():
        from django.contrib.auth import authenticate,login
        user = authenticate(username=loginForm.cleaned_data.get('userName'),password=loginForm.cleaned_data.get('password'))
        if user is not None and user.is_staff and user.is_active:
            login(request,user)
            return HttpResponseRedirect(reverse('mis_typist_list'))
        else:
            loginForm.errors['userName']=u'用户不存在！'
    
    return render_to_response(getTemplate('MIS_LOGIN')
                            ,{'form':loginForm}
                            ,context_instance=RequestContext(request))    

def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return HttpResponseRedirect('/')

def typist_list(request,current=None):
    '''
    凭证录入页面
    '''
    if request.method == 'GET':
        #upAudit = get_a_typist_list(current)
        
        upAudit = get_user_voucher(current)
        return render_to_response(getTemplate('MIS_TYPIST_INPUT'),
                                {'upAudit':upAudit},
                                context_instance=RequestContext(request))
    else:
        raise Http404

def get_user_voucher(current=None):
    '''
    获取一个用户上传的凭证信息
    '''
    if current is None:
        up = _up.objects.filter(state=UPGRADE_STATE.WAIT_AUDIT,need_typist=1,input_state=0).order_by('user_id','apply_level')[0:1]
    else:
        up = _up.objects.filter(state=UPGRADE_STATE.WAIT_AUDIT,need_typist=1,input_state=0,user_id__gt=current).order_by('user_id','apply_level')[0:1]

    voucherList = []
    if up and len(up) == 1 and up[0].user_id > 0:
        voucherList = _upVoucher.objects.filter(input_state=0,upgrade_id=up[0].id);

    kwargs = {}
    if len(voucherList) > 0:
        for voucher in voucherList:
            kwargs.setdefault(LICENSE_TYPE.get_form_by_type(voucher.cert_type),[]).append(voucher)

        kwargs['counter'] = len(kwargs)
        kwargs['owner'] = up[0].user_id
        kwargs['level'] = up[0].apply_level
        kwargs['up_id'] = up[0].id

    #pdb.set_trace()
    return kwargs;

def typist_input(request):
    '''
    #凭证录入action
    '''
    if request.method == 'POST':
        t,owner,level,upid= request.POST.get('__type',None),request.POST.get('__owner',None),request.POST.get('__level',None),request.POST.get('__upid',None)
        code,errors = 200,{}
        if t in globals() and owner is not None and level is not None:
            #pdb.set_trace()
            formType = globals()[t]
            formModel = formType(request.POST)
            if formModel.is_valid():
                model = formModel.save(commit=False)
                model.save(__currentUser=request.user,__owner=owner,__level=level,__upid=upid)
            else:
                code = 500
                errors = formModel.errors
        else:
            code = 403

        return HttpResponse(json.dumps({'statusCode':code,'errors':errors}));
    else: 
        raise Http404

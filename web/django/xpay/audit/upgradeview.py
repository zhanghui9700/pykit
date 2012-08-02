#coding=utf-8

import os,datetime,logging,pdb,json,string

from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden,Http404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from core.models import Person,SPerson,Merchant,UserProxy
from util.define import AccountType,UserType,LICENSE_TYPE,UPGRADE_SOURCE
from upgradeforms import CompanyBasicForm, PersonBasicForm,CompanyGoldForm
from util.imgstore import save_image,preview_img_response,remove_image
from audit.models import UpgradeVoucher,UpgradeVoucherProxy,UpgradeProxy,Upgrade

_logerror = logging.getLogger('my_error')
_loginfo = logging.getLogger('my_info')

def user_can_upgrade(user):
    '''
    是否可以发起升级请求
    '''
    upproxy = UpgradeProxy()
    return user.user_level < 2 and upproxy.can_upgrade(user)

def check_upgrade_state(view_func):
    def decorator(*args, **kwargs):
        request = args[0]
        is_wait_verify = user_can_upgrade(request.user)
        if not is_wait_verify:
            return render_to_response('msg/wait_verify_upgrade.html')
        return view_func(request)
    return decorator

UPGRADE_PAGE_INDEX = {'LevelType_0':'userportal/upgrade/upgrade_tiyan.html',
                      'LevelType_1':'userportal/upgrade/upgrade_jiben.html',
                      'LevelType_2':'userportal/upgrade/upgrade_huangjin.html',
                      'LevelType_3':'userportal/upgrade/upgrade_baijin.html'}

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
def upgrade_index(request):
    return HttpResponseRedirect('/account')
    '''
    用户升级页面，不同级别看到的模板是不一样的
    每个user_type在ControTable里有一些元数据信息，交易限额，费率，账期等
    '''
    user,level = request.user,request.user.user_level
    currentUserLevel = CoreLevel.objects.get(level=level)
    
    print currentUserLevel.monthamount

    #不同账号级别用不同的页面显示
    templatePath = UPGRADE_PAGE_INDEX.get(u'LevelType_%s' % AccountType.get_level_type(level),None) 
    if templatePath is None:
        raise Exception(u'没有获取到对应等级的升级页面,level:%s' % level)
    
    p = UserProxy.objects.get(pk=user.pk).get_xuser()
    context = {
        "person":p,
        "currentUserLevel":currentUserLevel,
        "can_upgrade":user_can_upgrade(request.user)
    }   
    return render_to_response(templatePath, context ,context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
def upgrade_upload(request):
    '''
    上传凭证页面
    '''
    if not user_can_upgrade(request.user):
        return HttpResponseRedirect('/upgrade')
    if request.method == 'POST':
        upProxy = UpgradeProxy()
        upgrade = Upgrade(user_id=request.user.id,
                          original_level = request.user.user_level,
                          up_source = UPGRADE_SOURCE.WEB,
                          apply_level = upProxy.get_next_level(request.user),
                          need_typist = 1,
                          input_state = 0)
         
        if not upProxy.is_valid(request.user,upgrade):
            raise Exception(u'凭证信息上传不够完整，怎么POST过来的数据？！uid:%s'% request.user.id)

        if upProxy.create_up(upgrade):
            return HttpResponseRedirect('/upgrade/waitaudit/')
    
    return render_to_response("userportal/upgrade/upload.html",context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
def upgrade_waitaudit(request):
    return render_to_response('msg/commit_image_success.html',{},context_instance=RequestContext(request))


def upgrade_remove_image(request):
    #pdb.set_trace()
    lc_name=request.GET['cert_name']
    remove_image(int(request.user.id),lc_name)
    result = False
    msg = ''
    return  

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
def upgrade_save_image(request):
    '''
    保存异步上传文件的action
    '''
    if request.method == 'POST':
        result,msg = False,u''
        try:
            for lc_name in request.FILES:
                lc_type  = LICENSE_TYPE.IMAGE_TYPE.get(lc_name.lower(),None)
                if lc_type is None:
                    raise Exception(u'不支持的凭证类型！')
                file = request.FILES[lc_name]
                ext = os.path.splitext(file.name)[1].lower()
                
                if ext not in LICENSE_TYPE.SUPPORTED_IMAGE:
                    raise Exception(u'图片类型错误，支持的图片类型%s' % string.join(LICENSE_TYPE.SUPPORTED_IMAGE,sep='|'))
                
                imgName = save_image(int(request.user.id),lc_name,file)
                voucherProxy = UpgradeVoucherProxy()
                upgradeProxy = UpgradeProxy()
                voucher = UpgradeVoucher(user_id=request.user.id,cert_type=lc_type,name=imgName,apply_level=upgradeProxy.get_next_level(request.user))

                if voucherProxy.save_voucher(voucher) < 1:
                    raise Exception(u'UpgradeVoucher save error!')
                else:
                    msg = imgName
                    result = True
        except Exception,e:
            _logerror.exception(e)
            msg = e.message

        return HttpResponse(json.dumps({'succeed':result,'msg':msg}))
    else:
        raise Exception('-----http post only!--------')

@user_passes_test(lambda u: u.is_authenticated(), login_url='/signin')
def voucher_preview(request,uid,scale,name):
    '''
    凭证预览
    uid = auth_user.id
    scale = small,middle,larget
    name = id_front.jpg|tax.jpg|license.jpg
    '''
    if request.method == 'GET':
        try:
            proxy = UpgradeVoucherProxy()
            voucher = proxy.get_voucher(uid=uid,name=name);
            if voucher is None:
                raise Exception(u'voucher not found!uid:%s,name:%s' % (uid,name))
        except Exception,e:
            _logerror.exception(e)
            uid = 0
            name = None 
        return preview_img_response(uid,name,scale)
    else:
        raise Exception('---http get only!---')

#!/usr/bin/env python
# -*- coding=utf-8 -*-

import pdb,re,logging

from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator,InvalidPage,EmptyPage
from django.contrib.auth.models import User

from core.models import Person,SPerson,Merchant,PersonProxy,SPersonProxy,MerchantProxy,UserProxy
from mis.models import Terminal,Psam
from util.define import UserType,TerminalUsedState,PsamUsedState,TerminalState,PsamState
from util.common import PageList

TEMPLATE_PATH = {'USER_SEARCH':'mis/user_search_list_v2.html',
                 'USER_DETAIL':'mis/user_search_detail.html',
                 'USER_TERMINAL_BIND':'mis/user_terminal_bind.html',
                 'USER_TERMINAL_BIND_SUCCESS':'mis/user_terminal_bind_success.html',
                 'USER_TERMINAL_BIND_STATE':'mis/user_terminal_bind_state.html'
                 }

_logerror = logging.getLogger('mis_error')

def search(request):
    '''
    用户列表查询页
    查询条件组合需要优化，目前是硬编码！
    '''
    if request.method == 'GET':
        number,name,lcnumber,idnumber,user_type,page = request.GET.get('number',None),request.GET.get('name',None),request.GET.get('lcnumber',None),request.GET.get('idnumber',None),request.GET.get('type','0'),request.GET.get('page',1)
        #pdb.set_trace() 
        type = int(user_type)
        if type == UserType.PERSON:
            userList = PersonProxy.objects.all()
            if number is not None and len(number)>0:
                userList = userList.filter(user__id=number)
            if name is not None and len(name) > 0:
                userList = userList.filter(username=name)
            if idnumber is not None and len(idnumber) >0:
                userList = userList.filter(id_number = idnumber)
        elif type == UserType.SPERSON or type == UserType.MERCHANT:
            if type == UserType.SPERSON:
                userList = SPersonProxy.objects.all()
            else:
                userList = MerchantProxy.objects.all() 
            if number is not None and len(number)>0:
                userList = userList.filter(user__id=number)
            if name is not None and len(name)>0:
                userList = userList.filter(company=name)
            if lcnumber is not None and len(lcnumber)>0:
                userList = userList.filter(license_number=lcnumber)
            if idnumber is not None and len(idnumber)>0:
                userList = userList.filter(id_number=idnumber)
        else:
            userList = None

        list_pages = None
        if userList is not None:
            print 'userList counter is %s' % len(userList)
            pager = Paginator(userList,15) 
            list_pages=PageList(pager.num_pages,page)
            try:
                userList = pager.page(page)
            except Exception,e:
                print e.message
                userList = pager.page(1)
        p = re.compile('&page=\d{1,}')
        link = p.sub('',request.get_full_path())
        srg = {'number':number or '',
               'name':name or '' ,
               'lcnumber':lcnumber or '',
               'idnumber':idnumber or '',
               'user_type':user_type}
        return render_to_response(TEMPLATE_PATH.get('USER_SEARCH'),{'userList':userList,'link':link,'pagenums':list_pages,'srg':srg},context_instance=RequestContext(request))
    else:
        raise Exception('http get only!')

def detail(request,uid=0):
    '''
    商户详情页面
    '''
    if request.method == 'GET':
        user = User.objects.get(pk=uid)
        core_user = None
        
        if user.user_type == UserType.PERSON:
            core_user = PersonProxy.objects.get(user__id=user.id)
        if user.user_type == UserType.SPERSON:
            core_user = SPersonProxy.objects.get(user__id=user.id)
        if user.user_type == UserType.MERCHANT:
            core_user = MerchantProxy.objects.get(user__id=user.id)

        viewdata = {'core_user':core_user}

        return render_to_response(TEMPLATE_PATH.get('USER_DETAIL'),viewdata,context_instance=RequestContext(request))
    else:
        raise Exception('http get only,what are you want to do!')

def bind_terminal(request,user_id = 0):
    user = UserProxy.objects.get(pk=user_id)
    core_user = user.get_xuser()
    
    if request.method == 'POST':
        terminalId = request.POST.get('terminalId',None)
        if terminalId is None:
            raise Exception('terminalid is null!uid:%s,terminalid:%s' % (user_id,terminalId))
        
        try:
            if bind(user,terminalId):
                return render_to_response(TEMPLATE_PATH.get('USER_TERMINAL_BIND_SUCCESS'),{},context_instance=RequestContext(request))
        except Exception,e:
            error = e.message

    return render_to_response(TEMPLATE_PATH.get('USER_TERMINAL_BIND'),{'core_user':core_user},context_instance=RequestContext(request))

def bind(user,terminalId):
    '''
    user = auto_user
    terminalid
    '''
    result = False
    terminalList = Terminal.objects.filter(pk=terminalId,\
        used = TerminalUsedState.AssignedPasmi,\
        state = TerminalState.Normal)
    
    if len(terminalList) == 1:
        terminal = terminalList[0]
        psamList = Psam.objects.filter(terminalid = terminal.id,used=PsamUsedState.Assigned,state = PsamState.Normal)
        if len(psamList) == 1:
            psam = psamList[0]
            tb = TerminalBind.objects.create(user = user.id,
                                        udid = user.id,
                                        terminalid = terminal.id,
                                        psamid = psam.id,
                                        psamtp = psam.psamtp,
                                        tckkey = terminal.tck,
                                        pinkey1 = psam.pinkey1,
                                        pinkey2 = psam.pinkey2,
                                        mackey = psam.mackey,
                                        diskey = terminal.diskey,
                                        fackey = u'%s%s' % (terminal.producer,terminal.model))
            if tb.pk > 0:
                terminal.update(user=user.id,used=TerminalUsedState.AssignedUser)
                psam.update(terminalid=terminal.id)
                result = True
            else:
                raise Exception(u'绑定读卡器失败，uid:%s,terminalid:%s,psam:%s' % (user.id,terminal.id,psam.id))

        else:
            raise Exception(u'读卡器找到了多个PSAM卡,terminalid:%s' % terminalId)
    else:
        raise Exception(u'此读卡器已被分配或者已作废,terminalid:%s' % terminalId)

    return result

def bind_state(request,user_id):
    if request.method == 'GET':
        return render_to_response(TEMPLATE_PATH.get('USER_TERMINAL_BIND_STATE'),{},context_instance=RequestContext(request))
    else:
        raise Exception('http get only!!!')

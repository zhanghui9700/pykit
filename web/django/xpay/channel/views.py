#!/bin/bash python
#-*- coding=utf-8 -*-

from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test

from audit.forms import LoginForm,UserForm,SPersonForm
from util.define import UserType

SIGNUP_TEMPLATE_ROOT = 'channel/signup' #$/template/channel/signup
MANAGE_TEMPLATE_ROOT = 'channel/manage' #$/template/channel/manage

@user_passes_test(lambda u: u.is_authenticated(), login_url='/login')
def apply_list(request):
    '''
    渠道管理-商户管理
    这里通过传递GET参数的方法区分需要查询数据
    '''
    return render_to_response('%s/apply_list.html'%MANAGE_TEMPLATE_ROOT,{},context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated(), login_url='/login')
def apply_basic(request):
    '''
    step1:基本信息
    #TODO:这里需要确认,如果渠道管理员注册流程未完成就关掉注册窗口，后续如何处理？\
    商户入网存在恶意添加注册信息的问题，造成大量手机号无法使用！
    '''
    userform = UserForm()
    if request.method == 'POST':
        return HttpResponseRedirect('/manage/apply/profile')
        userform = UserForm(request.POST)
        if userform.is_valid():
            user = userform.create_user()
            #TODO:cache current created user
            return HttpResponseRedirect(reverse('apply_profile_info'))

    return render_to_response('%s/signup.html'%SIGNUP_TEMPLATE_ROOT, 
                                {"userform": userform},
                                context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated(), login_url='/login')
def apply_profile(request):
    '''
    step2:商户扩展信息
    不同的商户类型需要导航到不同的注册模板页面
    ''' 
    if request.method == 'POST':
        return HttpResponseRedirect('/manage/apply/voucher')
    return render_to_response('%s/signup_sperson.html'%SIGNUP_TEMPLATE_ROOT,\
                             {'spersonform':SPersonForm()},context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated(), login_url='/login')
def apply_voucher(request):
    '''
    step3:上传凭证
    '''
    if request.method == 'POST':
        return HttpResponseRedirect('/manage/apply/feerate')
    return render_to_response('%s/signup3.html'%SIGNUP_TEMPLATE_ROOT,\
                             {},context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_authenticated(), login_url='/login')
def apply_feerate(request):
    '''step4:设置费率'''
    if request.method == 'POST':
        return HttpResponseRedirect('/manage/apply/feerate')
    return render_to_response('%s/signup4.html'%SIGNUP_TEMPLATE_ROOT,\
                             {},context_instance=RequestContext(request))
    
def login(request):
    '''渠道系统-登录，UserType==10'''
    if request.method == 'POST':
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            data = loginform.cleaned_data
            from django.contrib.auth import authenticate, login
            user = authenticate(username=loginform.cleaned_data['username'],\
                                password=loginform.cleaned_data['password'])
            if user and user.user_type == UserType.CHANNEL:
                login(request, user) 
                return HttpResponseRedirect('/manage/')

        return render_to_response('%s/login.html'%SIGNUP_TEMPLATE_ROOT,
                                      {'loginform': loginform, 'username':request.POST['username']},context_instance=RequestContext(request))
    else:
        return render_to_response('%s/login.html'%SIGNUP_TEMPLATE_ROOT, 
                                    {}, 
                                    context_instance=RequestContext(request))

def logout(request):
    '''渠道系统-退出'''
    from django.contrib.auth import logout
    logout(request)
    return HttpResponseRedirect('/login')


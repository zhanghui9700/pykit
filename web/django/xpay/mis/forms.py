#!/usr/bin/env python
#coding=utf-8
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from mis.models import *

class LoginForm(forms.Form):
    '''
    #登录页
    '''
    userName = forms.CharField(max_length=30,required=True)
    password = forms.CharField(max_length=128,required=True)

    def clean_userName(self):
        u   = self.data.get('userName',None)
        pwd = self.data.get('password',None)
        
        try:
            user = User.objects.get(username=u) 
        except:
            raise forms.ValidationError(u'您输入的用户名不存在！')

        if not user.check_password(pwd):
            raise forms.ValidationError(u'密码错误请重新输入！')

        if not user.is_active or not user.is_staff:
            raise forms.ValidationError(_(u'您输入的用户没有权限登录后台系统！'))
        
        return u
        
class IDCardInfoForm(ModelForm):
    '''
    #凭证录入-身份证
    '''
    class Meta:
        model = IDCardInfo

class TaxInfoForm(ModelForm):
    '''
    #凭证录入-税务登记证
    '''
    class Meta:
        model = TaxInfo

class ContractInfoForm(ModelForm):
    '''
    #凭证录入-房屋合同
    '''
    class Meta:
        model = ContractInfo

class OrgcodeInfoForm(ModelForm):
    '''
    #凭证录入-组织机构代码证
    '''
    class Meta:
        model = OrgcodeInfo
        
class LicenseInfoForm(ModelForm):
    '''
    #凭证录入-营业执照
    '''
    class Meta:
        model = LicenseInfo


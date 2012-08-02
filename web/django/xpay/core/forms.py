#!/usr/bin/env python
#coding=utf-8
import re,datetime,pdb
from django.utils.translation import gettext
from django.db.models import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from StringIO import StringIO
from django.conf import settings

from audit.models import VerifyCode
import models

my_errors={'required':_('输入不能为空')}

class ModifyForm(forms.Form):
    oldpassword = forms.CharField(max_length=20, label=_('老密码'), required=True,widget=forms.PasswordInput(attrs={'class':"varify_input"}),error_messages=my_errors)
    mobile = forms.CharField(max_length=11,label=_('手机号'),required=True,help_text=_('注册后不能修改'),widget=forms.TextInput(attrs={'readonly':'readonly','style':'color:#aaaaaa','tip':'只能输入数字'}),error_messages=my_errors)
    verifycode = forms.CharField(max_length=6,label=_('验证码'),required=True,help_text=_('注册后不能修改'), error_messages=my_errors,widget=forms.TextInput(attrs={'tip':'请输入验证码'}))
    password = forms.CharField(max_length=20,required=True,widget=forms.PasswordInput(),error_messages=my_errors)
    repassword = forms.CharField(max_length=20,label=_('设置密码'),required=True,widget=forms.PasswordInput(attrs={'class':"varify_input"}),help_text=_('六个以上字母、数字'),error_messages=my_errors)
    def clean_mobile(self):
        mobile = self.data.get('mobile')
        try:
            User.objects.get(mobile=mobile)
        except:    
            raise forms.ValidationError(_('错误的手机号'))
        print mobile
        return mobile

    def clean_verifycode(self):
        verifycode = self.data.get('verifycode')
        mobile = self.data.get('mobile')
        vc = VerifyCode.objects.filter(code=verifycode, mobile=self.data.get('mobile'),flag=0)
        if vc.count() != 1:
            raise forms.ValidationError(_('验证码不匹配，请检查是否输入正确'))
        for code in vc:
            if datetime.datetime.now()-code.created <= datetime.timedelta(minutes=5):
                return verifycode
        raise forms.ValidationError(_('验证码已经过期，请重新获取'))
 
    def clean_repassword(self):
        oldpwd = self.data.get('oldpassword')
        password,repassword = self.data.get('password'),self.data.get('repassword')

        if oldpwd == password:
            raise forms.ValidationError(_('新旧密码不能一样'))
        if password != repassword:
            raise forms.ValidationError(_('密码不一致'))
        print repassword
        return repassword
    def clean_password(self):
        pwd = self.data.get('password')

        if len(pwd)<6:
            raise forms.ValidationError(_('密码至少为六位'))
        return pwd

    def clean_oldpassword(self):
        mobile = self.data.get('mobile')
        try:
            user = User.objects.get(mobile=mobile)
        except:
            raise forms.ValidationError(_('错误的旧密码'))
        oldpwd = self.data.get('oldpassword')

        if not user.check_password(oldpwd):
            raise forms.ValidationError(_('错误的旧密码'))
        print oldpwd
        return oldpwd

class ResetForm(forms.Form):
    mobile = forms.CharField(max_length=11,label=_('手机号'),required=True, widget=forms.TextInput(),error_messages=my_errors)
    verifycode = forms.CharField(max_length=6,label=_('验证码'),required=True,widget=forms.TextInput(),error_messages=my_errors)
    password = forms.CharField(max_length=20,label=_('设置密码'),required=True,widget=forms.PasswordInput(),error_messages=my_errors)
    repassword = forms.CharField(max_length=20,label=_('设置密码'),required=True,widget=forms.PasswordInput(attrs={'class':"varify_input"}),error_messages=my_errors)
    def clean_mobile(self):
        mobile = self.data.get('mobile')
        if User.objects.filter(mobile=mobile).count() != 1:
            raise forms.ValidationError(_('该手机号尚未注册'))
        return mobile

    def clean_verifycode(self):
        verifycode = self.data.get('verifycode')
        mobile = self.data.get('mobile')
        vc = VerifyCode.objects.filter(code=verifycode, mobile=mobile,flag=0)
        if vc.count() < 1:
            raise forms.ValidationError(_('验证码不匹配，请检查是否输入正确'))
        for code in vc:
            if datetime.datetime.now()-code.created <= datetime.timedelta(minutes=5):
                return verifycode
        raise forms.ValidationError(_('验证码已经过期，请重新获取'))
            
    def clean_password(self):
        pwd = self.data.get('password')
        if len(pwd)<6:
            raise forms.ValidationError(_('密码至少六位'))
        return pwd

    def clean_repassword(self):
        oldpwd = self.data.get('oldpassword')
        password,repassword = self.data.get('password'),self.data.get('repassword')

        if oldpwd == password:
            raise forms.ValidationError(_('新旧密码不能一样'))
        if password != repassword:
            raise forms.ValidationError(_('密码不一致'))
        return repassword



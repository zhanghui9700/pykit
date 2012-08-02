#coding=utf-8
import re, datetime, pdb, Image, os
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.conf import settings
#from audit.models import UpgradeAudit

MIN_MSG_LEN = 5
MAX_IMG_SIZE = 5*1024*1024
MIN_IMG_SIZE = 1*1024*1024

CERT_TYPE ={
    'msg':0,
    'id_front':1,
    'id_back':2,
    'license':3,
    'tax':4,
    'public_account':5,
    'contract':6,
    'credit_card':7,
    'real_img':8
}

my_errors = {'required':'输入不能为空'}
#公司类用户申请基本级所需要填写的申请表单

def verify_uploaded_img(userid, level, type):
    int_type = CERT_TYPE.get(type)
    upgrades = None#UpgradeAudit.objects.filter(userid=int(userid), applylevel=level, certtype=int_type)
    if upgrades.count()<1:
        raise forms.ValidationError(u'请选择证件')
    path = settings.MEDIA_ROOT+`userid`
    path = path[:-1]
    path = path+'/'+upgrades[0].certextrainfo
    
    file_size = os.path.getsize(path)
    if file_size>MAX_IMG_SIZE:
        raise forms.ValidationError(u'证件图片过大')

class CompanyBasicForm(forms.Form):
    license = forms.ImageField(required=False, error_messages=my_errors)
    id_front = forms.ImageField(required=False, error_messages=my_errors)
    id_back = forms.ImageField(required=False, error_messages=my_errors)
    contract = forms.ImageField(required=False, error_messages=my_errors)
    reasons = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'class':'varify_input'}) ,error_messages=my_errors)

    def clean_license(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'license')
    
    def clean_id_front(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'id_front')
    
    def clean_id_back(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'id_back')
    
    def clean_contract(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'contract')

    def clean_reasons(self):
        reason = self.data.get('reasons')
        if len(reason)<MIN_MSG_LEN:
            raise forms.ValidationError(_('输入信息太少'))
        return reason

#个人类用户申请基本级时上传证件照片的表单
class PersonBasicForm(forms.Form):
    id_front = forms.ImageField(required=False)
    id_back = forms.ImageField(required=False)
    reasons = forms.CharField(max_length=140, widget=forms.TextInput(attrs={'class':'varify_input'}) ,error_messages=my_errors)

    def clean_reason(self):
        reason = self.data.get('reason')
        if len(reason)<MIN_MSG_LEN:
            raise forms.ValidationError(_('输入信息太少'))
        return reason

    def clean_id_front(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'id_front')
    
    def clean_id_back(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'id_back')

#公司类用户申请黄金用户时上传证件照片的表单
class CompanyGoldForm(forms.Form):
    license = forms.ImageField(required=False)
    id_front = forms.ImageField(required=False)
    id_back = forms.ImageField(required=False)
    public_account = forms.ImageField(required=False)
    contract = forms.ImageField(required=False)
    tax = forms.ImageField(required=False)
    contract = forms.ImageField(required=False)
    credit_card = forms.ImageField(required=False)
    real_img = forms.ImageField(required=False)

    def clean_license(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'license')
    
    def clean_id_front(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'id_front')
    
    def clean_id_back(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'id_back')
    
    def clean_public_account(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'public_account')
    
    def clean_tax(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'tax')

    def clean_contract(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'contract')
    
    def clean_credit_card(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'credit_card')
    
    def clean_real_img(self):
        userid = self.data.get('userid')
        level = self.data.get('level')
        verify_uploaded_img(userid, level, 'real_img')


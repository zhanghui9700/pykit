#!/usr/bin/env python
#coding=utf-8
import re, datetime, pdb
import json
import logging
from django.utils.translation import gettext
from django.db.models import ObjectDoesNotExist
from django.contrib.auth.models import User
#from django.utils.translation import gettext_lazy as _
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from StringIO import StringIO
from django.conf import settings
from models import Apply, ApplyCode, VerifyCode
from util.define import ApplyState,GROUP_ID,Patterns
from util.city import citylist

def _(msg):
    return msg

my_messages={'required':_(u'输入不能为空'),'max_length':_(u'请输入正确的手机号')}
_logger = logging.getLogger('my_error')

class UserForm(forms.Form):
    '''注册首页-基本信息'''
    applycode = forms.CharField(max_length=8, label=_('邀请码'), required=True, widget=forms.TextInput(attrs={'class':"varify_input required",'tip':"请输入您所获得的八位邀请码"}),error_messages=my_messages)
    user_type = forms.CharField(max_length=1)
    verifycode = forms.CharField(max_length=6, label=_('验证码'), required=True, widget=forms.TextInput(attrs={'tip': "请输入您收到的短信验证码"}),error_messages=my_messages)
    mobile = forms.CharField(max_length=11, label=_('手机号'),initial='', required=True, widget=forms.TextInput(attrs={'tip': "此手机号将作为登录账号",'class':'varify_input required'}),error_messages=my_messages)
    password = forms.CharField(max_length=20, label=_('设置密码'), required=True, widget=forms.PasswordInput(attrs={'tip': "请输入6-20个字符（数字、字母、特殊符号），区分大小写",'class':'varify_input required'}),error_messages=my_messages)
    repassword = forms.CharField(max_length=20, label=_('设置密码'), required=True, widget=forms.PasswordInput(attrs={'class':"varify_input required",'tip': "请重复您刚才输入的密码"}),error_messages=my_messages)

    def clean_mobile(self):
        mobile = self.data.get('mobile')
        pattern = Patterns['mobile']
        if not re.match(pattern, mobile):
            raise forms.ValidationError(_('无效手机号码'))
        if User.objects.filter(mobile=mobile).count() > 0:
            raise forms.ValidationError(_('该手机号已经注册'))
        return mobile

    def clean_applycode(self):
        applycode = self.data.get('applycode')
        try:
            ac = ApplyCode.objects.get(code=applycode)
        except:
            raise forms.ValidationError(u'邀请码不匹配,此邀请码重复或者不存在！')
        if ac.used < 1:
            raise forms.ValidationError(_('该邀请码已经被使用'))
        
        return applycode

    def clean_verifycode(self):
        verifycode = self.data.get('verifycode')
        pattern = '^[0-9]{6}$'
        if not re.match(pattern, verifycode):
            raise forms.ValidationError(_('无效验证码'))
        vc = VerifyCode.objects.filter(code=verifycode, mobile=self.data.get('mobile'),flag=0)
        if vc.count() > 0 and vc[0].flag == 1:
            raise forms.ValidationError(_('该验证码已经使用'))
        if not vc.count():
            raise forms.ValidationError(_('验证码不匹配，请检查是否输入正确'))
        if datetime.datetime.now()-vc[0].created>datetime.timedelta(minutes=5):
            raise forms.ValidationError(_('验证码已经过期，请重新获取'))
        return verifycode

    def clean_password(self):
        password = self.data.get('password')
        repassword = self.data.get('repassword')
        if password and len(password) < 6:
            raise forms.ValidationError(_('请输入6-20个字符长度的密码'))
        if ' ' in password:
            raise forms.ValidationError(_('密码不能包含空格'))
        if password != repassword:
            raise forms.ValidationError(_('两次输入的密码不一致'))
        return password

    def create_user(self,*args,**kwargs):
        now = datetime.datetime.now()
        data = self.cleaned_data
        applycode = ApplyCode.objects.get(code=data['applycode'])
        
        usertype = applycode.usertype
        if kwargs and 'user_type' in kwargs.keys():
            try:usertype = int(kwargs['user_type'])
            except:pass
        if usertype == 1:
            userlevel = 2
        elif usertype ==2 or usertype == 3:
            userlevel = 4
        else:
            userlevel =1
        try:ut = int(data.get('user_type','0'))>0 and data.get('user_type') or usertype
        except:ut=usertype
        user = User(username = data['mobile'], 
                        mobile = data['mobile'], 
                        email = ''+data['mobile'] + '@qfpay.com',
                        user_type = ut,
                        state = 1, 
                        is_staff = False, 
                        is_active = True, 
                        is_superuser = False, 
                        last_login = now,
                        date_joined = now,
                        user_level = 1)
        user.set_password(data['password'])
        user.save()

        if user.pk > 0:
            apl = self._create_apply(user)
            try:groupid = int(applycode.src)
            except:groupid = 10001
            apl.groupid = groupid
            apl.src = applycode.src
            apl.save()
            
            applycode.used = applycode.used - 1
            applycode.save()
            
            try:
                vs = VerifyCode.objects.filter(mobile=data['mobile'], code=data['verifycode']).update(flag=1)
            except:pass

        return user

    def _create_apply(self,user):
        '''子类需要重写此方法实现自己的逻辑'''
        apl = Apply.objects.create(user=user.id, 
                            mobile = user.username, 
                            usertype = user.user_type,
                            state = ApplyState.REGISTERED)
        return apl

class ShenmaUserForm(UserForm):
    '''注册首页-神码渠道'''
    group_user_name = forms.CharField(max_length=32, label=_('商桥网用户名'), required=True, widget=forms.TextInput(attrs={'class':"varify_input required",'tip':"请输入您的神州商桥网用户名"}),error_messages=my_messages)
    user_type = forms.CharField(required=False)
    
    def clean_applycode(self):
        applycode = self.data.get('applycode')
        try:
            ac = ApplyCode.objects.get(code=applycode)
        except:
            raise forms.ValidationError(u'邀请码不匹配,此邀请码重复或者不存在！')
        if ac.used < 1:
            raise forms.ValidationError(_('该邀请码已经被使用'))
        
        if ac.usertype != 3:
            raise forms.ValidationError(_('邀请码输入有误'))
        return applycode

    def _create_apply(self,user):
        ext = {}
        ext[u'商桥用户名']=self.cleaned_data.get('group_user_name',u'NULL')
        try:
            applycode = ApplyCode.objects.get(code=self.cleaned_data['applycode'])
            terminalid = applycode.terminalid
        except:
            terminalid = -1
        
        apl = None
        try:
            apl = Apply.objects.create(user = user.id, 
                                src = GROUP_ID.Shenma,
                                mobile = user.username, 
                                usertype = user.user_type,
                                tid = terminalid,
                                state = ApplyState.REGISTERED,
                                ext = json.dumps(ext))
        except Exception,ex:
            _logger.exception(ex)
        
        return apl 

class BaseApplyForm(forms.Form):
    '''
    申请表基类，最基本的信息可以定义在这里
    子类继承此base后添加自己的扩展字段即可
    每个子类需要实现3个方法来填充apply信息,这里使用了模版方法。
    ''' 
    #基本信息
    idnumber = forms.CharField(help_text=u'经营者身份证号',max_length=18,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请输入经营者身份证号"}),error_messages=my_messages)
    province = forms.CharField(help_text=u'经营省份',max_length=8,widget=forms.TextInput(attrs={'class':"varify_input",'tip': "请输入真实有效的信息"}),error_messages=my_messages)
    city = forms.CharField(help_text=u'经营城市',max_length=8,widget=forms.TextInput(attrs={'class':"varify_input",'tip': "请输入真实有效的信息"}),error_messages=my_messages)
    businessaddr = forms.CharField(help_text=u'经营地址',max_length=32,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请输入真实有效的信息"}),error_messages=my_messages)
    monthtradeamount = forms.IntegerField(help_text=u'月交易金额',required=False,widget=forms.TextInput(attrs={'class':"varify_input",'maxlength':"10",'tip':"请输入真实有效的信息（元为单位)"}))
    
    #联系人信息
    email = forms.EmailField(help_text=u'联系人邮箱',max_length=64,required=False,widget=forms.TextInput(attrs={'tip': "请填写正确的收据邮箱地址"}))
    mobile = forms.CharField(help_text=u'联系人手机',max_length=11,required=False,widget=forms.TextInput(attrs={'class':"varify_input required",'tip':"请输入联系人手机号"}),error_messages=my_messages) 
    telephone = forms.CharField(help_text=u'联系人固话',max_length=8,required=False,widget=forms.TextInput(attrs={'tip':"联系人电话,正确格式:010-12345678"}),error_messages=my_messages)
    telephoneregion = forms.CharField(help_text=u'区号',max_length=4,required=False,widget=forms.TextInput(attrs={'tip':"联系人电话,正确格式:010-12345678"}),error_messages=my_messages)

    #收款银行信息
    banknameprefix = forms.CharField(help_text=u'收款银行',max_length=32,widget=forms.TextInput(attrs={'class':"varify_input",'tip': "请输入真实有效的信息"}),error_messages=my_messages)
    bankname = forms.CharField(help_text=u'开户行支行名称',max_length=32,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请填写正确的银行地址"}),error_messages=my_messages)
    bankuser = forms.CharField(help_text=u'银行开户名称',max_length=32,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请填写正确的银行开户人姓名"}),error_messages=my_messages)
    bankaccount = forms.CharField(help_text=u'收款银行账号',max_length=32,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请输入16至32位的银行卡号"}),error_messages=my_messages)
    confirmbankaccount = forms.CharField(help_text=u'确认收款银行账号',max_length=32,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请重新输入银行卡号","oncopy":"return false;","onpaste":"return false;"}),error_messages=my_messages)
    
    def clean_monthtradeamount(self):
        monthtradeamount = self.data.get('monthtradeamount')
        if monthtradeamount:
            if len(monthtradeamount)>=10:
                raise forms.ValidationError(_('输入位数过长'))
            if len(monthtradeamount)==0:
                monthtradeamount='0'
            return int(monthtradeamount)
            


    def clean_idnumber(self):
        idnumber = self.data.get('idnumber')
        pattern = '^((1[1-5])|(2[1-3])|(3[1-7])|(4[1-6])|(5[0-4])|(6[1-5])|71|(8[12])|91)\d{4}((19\d{2}(0[13-9]|1[012])(0[1-9]|[12]\d|30))|(19\d{2}(0[13578]|1[02])31)|(19\d{2}02(0[1-9]|1\d|2[0-8]))|(19([13579][26]|[2468][048]|0[48])0229))\d{3}(\d|X|x)?$'
        if not re.match(pattern, idnumber):
            raise forms.ValidationError(_('无效身份证号'))
        return idnumber
     
    def clean_telephone(self):
        telephone = self.data.get('telephone')
        telephoneregion = self.data.get('telephoneregion')
        if telephone is None or len(telephone) == 0:
            if telephoneregion is None or len(telephoneregion) == 0:
                return ''
        pattern1 = '^(\d{2,3}-)?(\d{3}|\d{4})$'
        pattern2 = '^(\d{7,10})(-\d+)*$'
        if not re.match(pattern1, telephoneregion):
            raise forms.ValidationError(_('无效电话号码'))
        if not re.match(pattern2, telephone):
            raise forms.ValidationError(_('无效电话号码'))
        return telephone


    def clean_city(self):
        city = self.data.get('city')
        if city == u'-1':
            raise forms.ValidationError(_('请选择城市'))
        return city

    def clean_bankaccount(self):
        ba = self.data.get('bankaccount')
        pattern = '^\d{16,32}$'
        if not re.match(pattern, ba):
            raise forms.ValidationError(_('银行账号只能输入数字且为16-32位'))
        return ba
   
    def clean_confirmbankaccount(self):
        ba = self.data.get('confirmbankaccount')
        pattern = '^\d{16,32}$'
        if not re.match(pattern, ba):
            raise forms.ValidationError(_('银行账号只能输入数字且为16-32位'))
        if self.data.get('bankaccount') != ba:
            raise forms.ValidationError(_('两次银行账号输入不一致'))

        return ba

    def clean_name(self,ba):
        pattern =u'^[\u4e00-\u9fa5]+$'
        if not re.match(pattern,ba):
            return False
        else:
            return True
 
    def clean_bankname(self):
        bankname = self.data.get('bankname')
        if self.clean_name(bankname):
            return bankname
        else:
            raise forms.ValidationError(_('请输入正确的银行名称'))
    
    def clean_bankuser(self):
        bankuser = self.data.get('bankuser')
        if self.clean_name(bankuser):
            return bankuser
        else:
            raise forms.ValidationError(_('请输入正确的开户人姓名'))

    def clean_mobile(self):
        mobile = self.data.get('mobile')
        if mobile is None or len(mobile) == 0:
            raise forms.ValidationError(_('无效手机号码'))
        pattern = Patterns['mobile']
        if not re.match(pattern, mobile):
            raise forms.ValidationError(_('无效手机号码'))
        return mobile

    def _set_basic_info(self,apply):
        '''获取基本信息，给apply对象赋值'''
        raise Exception('not implemention,subclass must rewrite this method!')

    def _set_contact_info(self,apply):
        '''获取联系人信息'''

    def _set_payment_info(self,apply):
        '''获取付款信息'''
        data = self.cleaned_data
        apply.bankuser = data['bankuser']
        apply.bankname = data['banknameprefix']+data['bankname']
        apply.bankaccount = data['bankaccount']


    def save(self,apply,commit=True):
        '''保存申请表'''
        self._set_basic_info(apply)
        self._set_contact_info(apply)
        self._set_payment_info(apply)
        apply.state = ApplyState.COMMITINFO
        apply.save()

class BasePersonForm(BaseApplyForm):
    personname = forms.CharField(max_length=10,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请输入申请人的姓名"}),error_messages=my_messages)

    def clean_personname(self):
        personname = self.data.get('personname')
        if self.clean_name(personname):
            return personname
        else:
            raise forms.ValidationError(_('请输入您的中文姓名'))
    
    def _set_basic_info(self,apply):
        '''获取基本信息，给apply对象赋值'''
        data = self.cleaned_data
        apply.name = data['personname']
        apply.idnumber = data['idnumber']
        apply.businessaddr = str(citylist[int(data['province'])]['n']+citylist[int(data['province'])]['c'][int(data['city'])]).decode('utf8')+data['businessaddr'] 
        apply.legalperson = apply.name
        apply.address = apply.businessaddr
        apply.monthtradeamount = data['monthtradeamount']
        apply.terminalcount = 1
    
    def _set_contact_info(self,apply):
        '''获取联系人信息'''
        data = self.cleaned_data
        apply.contact =  data['personname']
        apply.email = data['email']
        apply.mobile = data['mobile']
        apply.telephone = data['telephoneregion']+data['telephone']
      
class PersonForm(BasePersonForm):
    '''钱方直营-个人申请表'''
    pass

class SMPersonForm(BasePersonForm):
    '''神码渠道-个人申请表'''
    pass 

class BaseSPersonForm(BaseApplyForm):
    '''申请表-个体户'''
    mcc = forms.CharField(help_text=u'出售的商品或服务',max_length=32,widget=forms.Textarea(attrs={'class':"varify_input required",'tip': "请输入真实有效的信息"}),error_messages={'required':_(u'输入不能为空'),'max_length':_(u'长度必须限制在32个字符以内')})
    nickname = forms.CharField(help_text=u'收据显示名称',max_length=64,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请填写收据显示名称"}),error_messages=my_messages)
    shopname = forms.CharField(help_text=u'字号名称',max_length=32,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请输入真实的字号信息"}),error_messages=my_messages)
    legalperson = forms.CharField(help_text=u'法人(联系人)',max_length=32,required=False,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请输入经营者姓名"}))
    licensenumber = forms.CharField(help_text=u'营业执照号',required=True,max_length=20,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请输入真实有效的信息"}),error_messages=my_messages)
    terminalcount = forms.IntegerField(error_messages=my_messages)

    def clean_licensenumber(self):
        licensenumber = self.data.get('licensenumber')
        pattern = '^\d*$'
        if not re.match(pattern, licensenumber):
            raise forms.ValidationError(_('只能输入数字'))
        else:
            return licensenumber

    def clean_shopname(self):
        shopname = self.data.get('shopname')
        if self.clean_name(shopname):
            return shopname
        else:
            raise forms.ValidationError(_('请输入正确的公司企业名称'))
 
    def clean_legalperson(self):
        legalperson = self.data.get('legalperson')
        if self.clean_name(legalperson):
            return legalperson
        else:
            raise forms.ValidationError(_('请输入正确的法人姓名'))
    
    def _set_basic_info(self,apply):
        '''获取基本信息，给apply对象赋值'''
        data = self.cleaned_data
        
        apply.name = data['shopname']
        apply.idnumber = data['idnumber']
        apply.businessaddr = str(citylist[int(data['province'])]['n']+citylist[int(data['province'])]['c'][int(data['city'])]).decode('utf8')+data['businessaddr'] 
        apply.legalperson = data['legalperson']
        apply.address = apply.businessaddr
        apply.mcc = data['mcc']
        apply.monthtradeamount = data['monthtradeamount']
        apply.nickname=data['nickname']
        apply.licensenumber = data['licensenumber']
        apply.terminalcount = data['terminalcount']
    
    def _set_contact_info(self,apply):
        '''获取联系人信息'''
        data = self.cleaned_data
        apply.contact = data['legalperson']
        apply.mobile = data['mobile']
        apply.telephone = data['telephoneregion']+data['telephone']
        apply.email = data['email']

class SPersonForm(BaseSPersonForm):
    '''钱方直营-个体户申请表'''
    pass
class SMSPersonForm(BaseSPersonForm):
    '''神码渠道-个体户申请表'''
    pass

class BaseCompanyForm(BaseApplyForm):
    '''公司申请表'''
    mcc = forms.CharField(help_text=u'出售的商品或服务',max_length=32,widget=forms.Textarea(attrs={'class':"varify_input required",'tip': "请输入真实有效的信息"}),error_messages={'required':_(u'输入不能为空'),'max_length':_(u'长度必须限制在32个字符以内')})
    nickname = forms.CharField(help_text=u'收据显示名称',max_length=64,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请填写收据显示名称"}),error_messages=my_messages)
    company = forms.CharField(max_length=32,widget=forms.TextInput(attrs={'class':"varify_input required",'tip':"请输入企业的中文名称"}), error_messages=my_messages)
    legalperson = forms.CharField(max_length=32,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请输入法人信息"}),error_messages=my_messages)
    licensenumber = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请输入营业执照编号"}),error_messages=my_messages)
    tprovince = forms.CharField(max_length=8,required=False,widget=forms.TextInput(attrs={'class':"varify_input",'tip': "请输入经营省份"}),error_messages=my_messages)
    tcity = forms.CharField(max_length=8,required=False,widget=forms.TextInput(attrs={'class':"varify_input",'tip': "请输入经营城市"}),error_messages=my_messages)
    tradeaddr = forms.CharField(max_length=32,required=False,widget=forms.TextInput(attrs={'class':"varify_input required",'tip': "请输入经营地址"}),error_messages=my_messages)
    contact = forms.CharField(max_length=6,widget=forms.TextInput(attrs={'class':"varify_input required",'tip':"请输入联系人姓名"}),error_messages=my_messages)
    terminalcount = forms.IntegerField(error_messages=my_messages)
    
    def clean_contact(self):
        contact = self.data.get('contact')
        if self.clean_name(contact):
            return contact
        else:
            raise forms.ValidationError(_('请输入联系人中文名称'))


    def clean_legalperson(self):
        legalperson = self.data.get('legalperson')
        if self.clean_name(legalperson):
            return legalperson
        else:
            raise forms.ValidationError(_('请输入法人中文名称'))

    def clean_licensenumber(self):
        licensenumber = self.data.get('licensenumber')
        pattern = '^\d*$'
        if not re.match(pattern, licensenumber):
            raise forms.ValidationError(_('只能输入数字'))
        else:
            return licensenumber

    def clean_company(self):
        company = self.data.get('company')
        if self.clean_name(company):
            return company
        else:
            raise forms.ValidationError(_('请输入正确的公司企业名称')) 
            
    def _set_basic_info(self,apply):
        data = self.cleaned_data
        apply.name = data['company']
        apply.nickname = data['nickname']
        apply.legalperson = data['legalperson']
        apply.idnumber = data['idnumber']
        
        apply.businessaddr = str(citylist[int(data['province'])]['n']+citylist[int(data['province'])]['c'][int(data['city'])]).decode('utf8') + data['businessaddr']
        apply.address = str(citylist[int(data['tprovince'])]['n']+citylist[int(data['tprovince'])]['c'][int(data['tcity'])]).decode('utf8') + data['tradeaddr']
        
        apply.licensenumber = data['licensenumber']
        apply.mcc = data['mcc']
        apply.monthtradeamount = data['monthtradeamount']
        apply.terminalcount = data['terminalcount']        

    def _set_contact_info(self,apply):
        data = self.cleaned_data
        apply.contact = data['contact']
        apply.mobile = data['mobile']
        apply.telephone = data['telephoneregion']+data['telephone']

class CompanyForm(BaseCompanyForm):
    '''钱方直营-公司申请表'''
    pass 
class SMCompanyForm(BaseCompanyForm):
    '''神马渠道-公司申请表'''
    def _set_basic_info(self,apply):
        super(type(self),self)._set_basic_info(apply)
        apply.groupid = GROUP_ID.Shenma
   
class LoginForm(forms.Form):
    username = forms.CharField(max_length=11, label=_('邮箱或手机号'), required=True, error_messages=my_messages)
    password = forms.CharField(max_length=24, label=_('密码'), required=True, widget=forms.PasswordInput, error_messages=my_messages)

    def clean_username(self):
        try:
            username = self.data.get('username')
            m = re.search(u'[a-zA-Z0-9\.]+@[a-zA-Z0-9]+\.[a-zA-Z]+', username)
            if m and m.group(0):
                user = User.objects.get(email=m.group(0))
            else:
                user = User.objects.get(username=self.data.get('username'))
        except ObjectDoesNotExist:
            raise forms.ValidationError(_('该用户不存在'))
        return user.username

    def clean_password(self):
        try:
            from django.contrib.auth import authenticate
            user = authenticate(username=self.cleaned_data.get('username'), password=self.cleaned_data.get('password'))
            if not user:
                raise forms.ValidationError(_('用户名或密码错误'))
        except ObjectDoesNotExist:
            raise forms.ValidationError(_('用户名或密码错误'))
        return self.data.get('password')

class ApplyPassForm(forms.Form):
    deposit_amount = forms.IntegerField(label=u'借记卡限额',help_text=u'必填，借记卡限额，只能用数字，范围（1~32767），单位是：百元。如限额是1000元，只需输入10')
    credit_amount = forms.IntegerField(label=u'信用卡限额',help_text=u'必填，信用卡限额，只用数字，范围（1~32767），单位是：百元。如限额是1000元，只需输入10')

    channel_name = forms.CharField(max_length=256,label=u'绑定交易渠道')
    mcc = forms.CharField(max_length=4,label=u'mcc',required=True)
    
    deposit_rate = forms.FloatField(label=u'设置借记卡费率',required=True)
    credit_rate = forms.FloatField(label=u'设置信用卡费率',required=True)
    
    fee_max = forms.FloatField(label=u'设置封顶额度',required=True)

    
    def _isInt(self,s):
        try:
            num = int(s)
            return True
        except:
            raise forms.ValidationError('此字段必须为数字！')
    
    def _inRange(self,num,min,max):
        num = int(num)
        if num >= min and num <= max:
            return True
        else:
            raise forms.ValidationError('字段越界')

    def clean_deposit_amount(self):
        _amt = self.data.get('deposit_amount')
        #pdb.set_trace() 
        if self._isInt(_amt) and self._inRange(_amt,1,32767):
            return _amt
        
    def clean_credit_amount(self):
        _amt = self.data.get('credit_amount')
        
        if self._isInt(_amt) and self._inRange(_amt,1,32767):
            return _amt

    def clean_mcc(self):
        _mcc = self.data.get('mcc')
        try:
            _mcc = int(_mcc)
            if _mcc < 1:
                raise
        except:
            raise forms.ValidationError('mcc代码必须为数字！')
        return _mcc

    def clean_deposit_rate(self):
        _rate = self.data.get('deposit_rate')
        return _rate

    def clean_credit_rate(self):
        _rate = self.data.get('credit_rate')

        return _rate

    def clean_fee_max(self):
        _fee = self.data.get('fee_max')
        try:
            _fee = float(_fee)
        except:
            raise forms.ValidationError(u'请输入正确的金额，可以保留到小数点后两位')
        
        return _fee

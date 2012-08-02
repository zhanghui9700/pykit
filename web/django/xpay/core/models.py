#!/usr/bin/env python
#coding=utf-8
# Copyright 2011
# Author fengyong@qfpay.net

from django.contrib.auth.models import User
from django.db import models
from settle.models import Account
from util.define import UserType,AccountType,UserState,ApplyState
# Create your models here.

from util.define import GROUP_CHOICES

def basedisplay_creditratio(self):
    acc = Account.objects.filter(userid = self.user.id)
    if acc:
        return acc[0].creditratio
    else:
        return ''

def basedisplay_feeratio(self):
    acc = Account.objects.filter(userid = self.user.id)
    if acc:
        return acc[0].feeratio
    else:
        return ''

class Person(models.Model):
    user = models.ForeignKey(User,db_column="userid")
    username = models.CharField(u'申请人姓名',max_length=32,null=True,blank=True)
    nickname = models.CharField(u'品牌名称',max_length=64,blank=True,null=True)
    id_number = models.CharField(u'身份证号',max_length=18,blank=True,null=True)
    id_start_date = models.DateField(u'身份证凭证有效期开始时间',blank=True,null=True)
    id_end_date = models.DateField(u'身份证凭证有效期终止时间',blank=True,null=True)
    id_photo1 = models.ImageField(u'身份证正面',upload_to="userinfo/",blank=True)
    id_photo2 = models.ImageField(u'身份证反面',upload_to="userinfo/",blank=True)
    address = models.CharField(u'个人注册地址',max_length=256,blank=True,null=True)
    latitude = models.FloatField(u'纬度',blank=True,null=True)
    longitude = models.FloatField(u'经度',blank=True,null=True)
    city = models.CharField(u'所在城市',max_length=32,blank=True,null=True)
    telephone = models.CharField(u'固定电话',max_length=32,blank=True,null=True)
    mobile = models.CharField(u'移动电话',max_length=20,blank=True,null=True)
    email = models.EmailField(u'电子邮箱地址',max_length=75,blank=True,null=True)
    post = models.CharField(u'邮编',max_length=10,blank=True,null=True)
    mcc = models.CharField(u'商户类别MCC',max_length=4,blank=True,null=True,default='7399')
    bank_name = models.CharField(u'开户银行网点',max_length=64,blank=True,null=True)#银行
    bankuser = models.CharField(u'开户名',max_length=32,null=True) #开户人姓名
    bank_account = models.CharField(u'银行账号',max_length=32,blank=True,null=True)#银行帐号
    credit_bank = models.CharField(u'个人信用卡行',max_length=64,blank=True,null=True)
    credit_card = models.CharField(u'个人信用卡行账号',max_length=20,blank=True,null=True)#信用卡号
    edu = models.SmallIntegerField(u'教育水平',blank=True,null=True,default=1)#教育背景
    month_income = models.SmallIntegerField(u'月收入',default=0,blank=True,null=True)
    month_expense = models.SmallIntegerField(u'月支出',default=0,blank=True,null=True)
    allowed_trade = models.IntegerField(u'可交易类型',default=15,blank=True,null=True)
    allowed_time = models.IntegerField(u'交易时间段',default=7,blank=True,null=True)
    allowed_card = models.IntegerField(u'交易可允许卡别',default=15,blank=True,null=True)
    allowed_currency = models.IntegerField(u'交易可使用币别',default=3,blank=True,null=True)
    allowed_amount = models.IntegerField(u'单笔上限',default=500000,blank=True,null=True)
    last_modify = models.DateField(u'最后变更时间',auto_now_add=True,blank=True,null=True,auto_now=True)
    last_admin = models.IntegerField(u'最后变更人ID',blank=True,null=True)
    class Meta:
        db_table = 'core_person'
        #app_label= u'usermanager'
        verbose_name_plural = u'个人'
    
    def trans_last_modify(self):
        return self.last_modify
    trans_last_modify.short_description='最后变更时间'
    trans_last_modify.admin_order_field='last_modify'
    def display_userid(self):
        return self.user.id
    display_userid.short_description = 'userid'

    def display_creditratio(self):
        return basedisplay_creditratio(self)
    display_creditratio.short_description = '信用卡费率'
    def display_feeratio(self):
        return basedisplay_feeratio(self)
    display_feeratio.short_description = '储值卡费率'
 
    def display_user_level(self):
        return self.user.user_level
    display_user_level.short_description=u'商户等级'

class SPerson(models.Model):
    user = models.ForeignKey(User,db_column="userid")
    company = models.CharField(u'公司名称',max_length=64,null=True) #商户名称
    nickname = models.CharField(u'品牌名称',max_length=64,blank=True,null=True)
    legal_person = models.CharField(u'法人',max_length=32,null=True)
    id_number = models.CharField(u'法人身份证号',max_length=18,null=True)
    id_stat_date = models.DateField(u'法人身份证凭证有效期开始时间',blank=True,null=True)
    id_end_date = models.DateField(u'法人身份证凭证有效期终止时间',blank=True,null=True)
    id_photo1 = models.ImageField(u'法人身份证正面',upload_to="userinfo/",blank=True,null=True)
    id_photo2 = models.ImageField(u'法人身份证反面',upload_to="userinfo/",blank=True,null=True)
    license_number = models.CharField(u'公司营业执照号',max_length=20,blank=True,null=True) #营业执照号
    license_end_date = models.DateField(u'营业执照凭证有效期至',blank=True,null=True)
    license_photo = models.ImageField(u'公司营业执照凭证',upload_to="userinfo/",blank=True,null=True)
    tax_number = models.CharField(u'税务号',max_length=40,blank=True,null=True)
    tax_end_date = models.DateField(u'税务凭证有效期至',blank=True,null=True)
    tax_photo = models.ImageField(u'税务凭证',upload_to="userinfo/",blank=True,null=True)
    orgcode = models.CharField(u'机构号',max_length=20,blank=True,null=True)
    #address = models.CharField(max_length=256,blank=True)
    business_addr = models.CharField(u'公司经营地址',max_length=256,blank=True,null=True)
    latitude = models.FloatField(u'纬度',blank=True,null=True)
    longitude = models.FloatField(u'经度',blank=True,null=True)
    city = models.CharField(u'公司所在城市',max_length=32,blank=True,null=True)
    contact = models.CharField(u'公司联系人',max_length=32,blank=True,null=True)
    telephone = models.CharField(u'公司固定电话',max_length=32,blank=True,null=True)
    mobile = models.CharField(u'公司手机号码',max_length=20,blank=True,null=True)
    email = models.EmailField(u'公司电子邮箱地址',max_length=75,blank=True,null=True)
    post = models.CharField(u'邮编',max_length=10,blank=True,null=True)
    mcc = models.CharField(u'商户类别MCC',max_length=4,blank=True,null=True)
    bankname = models.CharField(u'开户银行网点',max_length=64,blank=True,null=True)
    bankuser = models.CharField(u'开户名',max_length=32,blank=True,null=True) #开户人姓名
    bankaccount = models.CharField(u'公司银行账号',max_length=32,blank=True,null=True)
    creditbank = models.CharField(u'个人信用卡行',max_length=64,blank=True,null=True)
    creditcard = models.CharField(u'个人信用卡行账号',max_length=20,blank=True,null=True)
    month_turnover = models.IntegerField(u'月营业额',default=0,blank=True,null=True)
   
    allowed_trade = models.IntegerField(u'可交易类型',default=15,blank=True,null=True)
    allowed_time = models.IntegerField(u'交易时间段',default=7,blank=True,null=True)
    allowed_card = models.IntegerField(u'交易可允许卡别',default=15,blank=True,null=True)
    allowed_currency = models.IntegerField(u'交易可使用币别',default=3,blank=True,null=True)
    allowed_amount = models.IntegerField(u'单笔上限',default=500000,blank=True,null=True)
    
    last_modify = models.DateField(u'最后变更时间',auto_now_add=True)
    last_admin = models.IntegerField(u'最后变更人ID')
        
    class Meta:
        db_table = 'core_sperson'
        #app_label= u'usermanager'
        verbose_name_plural = u'个体户'

    def display_creditratio(self):
        return basedisplay_creditratio(self)
    display_creditratio.short_description = '信用卡费率'
    def display_feeratio(self):
        return basedisplay_feeratio(self)
    display_feeratio.short_description = '储值卡费率'
    def display_userid(self):
        return self.user.id
    display_userid.short_description = 'userid'
    def display_user_level(self):
        return self.user.user_level
    display_user_level.short_description=u'商户等级'

class Merchant(models.Model):
    user = models.ForeignKey(User, db_column="userid")
    company = models.CharField(u'公司名称',max_length=64) #商户名称
    nickname = models.CharField(u'品牌名称',max_length=64,blank=True,null=True)
    legal_person = models.CharField(u'法人',max_length=32)
    id_number = models.CharField(u'法人身份证号',max_length=18)
    id_stat_date = models.DateField(u'法人身份证凭证有效期开始时间',blank=True)
    id_end_date = models.DateField(u'法人身份证凭证有效期终止时间',blank=True)
    id_photo1 = models.ImageField(u'法人身份证正面',upload_to="userinfo/",blank=True) #企业法人身份证照片
    id_photo2 = models.ImageField(u'法人身份证反面',upload_to="userinfo/",blank=True) #
    license_number = models.CharField(u'公司营业执照号',max_length=20,blank=True) #营业执照号
    license_end_date = models.DateField(u'营业执照凭证有效期至',blank=True)
    license_photo = models.ImageField(u'公司营业执照凭证',upload_to="userinfo/",blank=True) #营业执照
    tax_number = models.CharField(u'税务号',max_length=40,blank=True)
    tax_end_date = models.DateField(u'税务凭证有效期至',blank=True)
    tax_photo = models.ImageField(u'税务凭证',upload_to="userinfo/",blank=True) #税务登记证
    orgcode = models.CharField(u'机构号',max_length=20,blank=True)
    #address = models.CharField(max_length=256,blank=True)
    business_addr = models.CharField(u'公司经营地址',max_length=256,blank=True)
    latitude = models.FloatField(u'纬度',blank=True)
    longitude = models.FloatField(u'经度',blank=True)
    city = models.CharField(u'公司所在城市',max_length=32,blank=True)
    contact = models.CharField(u'公司联系人',max_length=32,blank=True)
    telephone = models.CharField(u'公司固定电话',max_length=32,blank=True)
    mobile = models.CharField(u'公司手机号码',max_length=20,blank=True)
    email = models.EmailField(u'公司电子邮箱地址',max_length=75,blank=True)
    post = models.CharField(u'邮编',max_length=10,blank=True)
    mcc = models.CharField(u'商户类别MCC',max_length=4)
    bankname = models.CharField(u'开户银行网点',max_length=64,blank=True)
    bankuser = models.CharField(u'开户名',max_length=32,blank=True,null=True) #开户人姓名
    bankaccount = models.CharField(u'公司银行账号',max_length=32,blank=True)
    creditbank = models.CharField(u'个人信用卡行',max_length=64,blank=True)
    creditcard = models.CharField(u'个人信用卡行账号',max_length=20,blank=True)
    month_turnover = models.IntegerField(u'月营业额',default=0,blank=True)
    
    allowed_trade = models.IntegerField(u'可交易类型',default=15,blank=True,null=True)
    allowed_time = models.IntegerField(u'交易时间段',default=7,blank=True,null=True)
    allowed_card = models.IntegerField(u'交易可允许卡别',default=15,blank=True,null=True)
    allowed_currency = models.IntegerField(u'交易可使用币别',default=3,blank=True,null=True)
    allowed_amount = models.IntegerField(u'单笔上限',default=500000,blank=True,null=True)
    
    last_modify = models.DateField(u'最后变更时间',auto_now_add=True)
    last_admin = models.IntegerField(u'最后变更人ID')
    
    class Meta:
        db_table='core_merchant'
        #app_label= u'usermanager'
        verbose_name_plural = u'商户'

    def display_creditratio(self):
        return basedisplay_creditratio(self)
    display_creditratio.short_description = '信用卡费率'
    def display_feeratio(self):
        return basedisplay_feeratio(self)
    display_feeratio.short_description = '储值卡费率'
    def display_userid(self):
        return self.user.id
    display_userid.short_description = 'userid'
    def display_user_level(self):
        return self.user.user_level
    display_user_level.short_description=u'商户等级'



class TerminalBind(models.Model):
    STATE_CHOICE = ((1,u'未绑定'),
        (2,u'正常'),
        (3,u'激活未成功'),
        (4,u'失效'))
    user = models.ForeignKey(User,db_column='userid')
    udid = models.CharField(u'手机编号',max_length=40,default='1')
    terminalid = models.CharField(u'设备编号',max_length=20)
    psamid = models.CharField(u'PSAM卡号',max_length=8)
    psamtp = models.CharField(u'PSAM卡加密类型',max_length=2,default='1')
    tckkey = models.CharField(u'刷卡TCK密文',max_length=32,default='0EA08C852B9653F76DB4A90612850CBD')
    pinkey1 = models.CharField(u'解密因子（PIN母密钥1）',max_length=32,default='FC003F7139AEA8AA85F89319C0333658')
    pinkey2 = models.CharField(u'解密因子（PIN母密钥2）',max_length=32,default='97F30539FF3CA379FE4C606608D5A128')
    mackey = models.CharField(u'解密因子（MAC母密钥）',max_length=32,default='DD090BA53E64C6B00462CDDBB30FC857')
    diskey = models.CharField(u'解密因子（BANKID）',max_length=16,default='65600001')
    fackey = models.CharField(u'厂商码',max_length=16,default='00010001')
    os = models.SmallIntegerField(u'操作系统类型',default=1)
    os_ver = models.CharField(u'操作系统版本',max_length=32,default='4.0.2')
    active_date = models.DateTimeField(u'激活日期',auto_now_add=True)
    state = models.SmallIntegerField(u'状态',default=2, choices=STATE_CHOICE)
    class Meta:
        db_table = 'termbind'
        #app_label= u'usermanager'
        verbose_name_plural = u'读卡器绑定'

    def display_userid(self):
        return self.user.id
    display_userid.short_description = 'userid'

class Cardbin(models.Model):
    bankname = models.CharField(max_length=32)
    bankid = models.CharField(max_length=8)
    cardcd = models.CharField(max_length=19)
    cardlen = models.SmallIntegerField()
    cardbin = models.CharField(max_length=10)
    cardname = models.CharField(max_length=64)
    cardtp = models.CharField(max_length=2)
    cardorg = models.CharField(max_length=2)
    foreign = models.SmallIntegerField()
    class Meta:
        db_table = 'cardbin'

class Profile(models.Model):
    TYPE_CHOICES = (
        (1,u'个人'),
        (2,u'个体户'),
        (3,u'公司'),
    )

    NEEDAUTH_CHOICES = (
        (1,u'是'),
        (2,u'否'),
    )

    PASSCHECK_CHOICES = (
        (1,u'是'),
        (2,u'否'),
    )

    BANKTYPE_CHOICES = (
        (1,u'对私'),
        (2,u'对公'),
    )

    ALLOWAREA_CHOICES = (
        (0,u'本市'),
        (1,u'全国'),
    )

    IS_DEVELOPER_CHOICES = (
        (1,u'是'),
        (2,u'否'),
    )


    user = models.ForeignKey(User,db_column="userid")
    nickname = models.CharField(u'收款收据显示名称',max_length=64,blank=True,null=True)
    name = models.CharField(u'用户名',max_length=32,help_text=u'个人申请人姓名/个体户字号/商户注册名',blank=True,null=True)
    idnumber = models.CharField(u'身份证号',max_length=20,help_text=u'申请人身份证号/法人代表身份证号/法人代表身份证号',blank=True,null=True)
    idenddate = models.DateField(u'身份证到期日',help_text=u'身份证到期日/法人身份证到期日/法人身份证到期日',blank=True,null=True)
    type = models.SmallIntegerField(u'商户类型',choices=TYPE_CHOICES)
    provision = models.CharField(u'售卖的商品或服务',max_length=256,blank=True,null=True)
    province = models.CharField(u'营业地址所在省',max_length=10,blank=True,null=True)
    city = models.CharField(u'营业地址所在市',max_length=32,blank=True,null=True)
    terminalcount = models.CharField(u'终端数量',max_length=1,blank=True,null=True)
    logisticaddr = models.CharField(u'读卡器配送地址',max_length=256,blank=True,null=True)
    
    banktype = models.SmallIntegerField(u'清算银行类型',choices=BANKTYPE_CHOICES)
    bankname = models.CharField(u'清算银行名称',max_length=256,blank=True,null=True)
    bankuser = models.CharField(u'清算资金账户名称',max_length=32,blank=True,null=True)
    bankaccount = models.CharField(u'清算资金账号',max_length=32,blank=True,null=True)
    
    mobile = models.CharField(u'联系人电话号码',max_length=11,blank=True,null=True)
    allowarea = models.SmallIntegerField(u'开通区域',default=0,choices=ALLOWAREA_CHOICES)
    businessaddr = models.CharField(u'营业地址',max_length=256,blank=True,null=True)
    address = models.CharField(u'公司注册地址',max_length=256,blank=True,null=True)
    post = models.CharField(u'邮编',max_length=10,blank=True,null=True)
    telephone = models.CharField(u'联系固话（经营场所联系电话）',max_length=32,blank=True,null=True)
    
    email = models.EmailField(u'商户电邮',max_length=75,blank=True,null=True)
    area = models.FloatField(u'店面面积',default=100.0,blank=True,null=True)
    tid = models.CharField(u'终端号',max_length=256,blank=True,null=True)
    mcc = models.CharField(u'商户类别MCC',max_length=32,blank=True,null=True)
    org_code = models.CharField(u'机构号',max_length=20,blank=True,null=True)
    longitude = models.FloatField(u'经度',blank=True,null=True)
    latitude = models.FloatField(u'纬度',blank=True,null=True)
    memo = models.TextField(u'备注json（扩展字段）',blank=True,null=True)

    needauth = models.SmallIntegerField(u'是否需要授权',blank=True,null=True,choices=NEEDAUTH_CHOICES)
    licensenumber = models.CharField(u'营业执照注册号',max_length=20,blank=True,null=True)
    legalperson = models.CharField(u'法人代表姓名',max_length=32,blank=True,null=True)
    licenseend_date = models.DateField(u'营业执照到期日',blank=True,null=True)
    taxnumber = models.CharField(u'税务登记号',max_length=40,blank=True,null=True)
    contact = models.CharField(u'联系人',max_length=32,blank=True,null=True)

    passcheck = models.SmallIntegerField(u'营业执照是否通过年检',choices=PASSCHECK_CHOICES,blank=True,null=True)
    founddate = models.DateField(u'公司成立年份',blank=True,null=True)
    groupid = models.IntegerField(u'渠道',default='10001',choices=GROUP_CHOICES)
    
    allowed_trade = models.IntegerField(u'可交易类型',default=15,blank=True,null=True)
    allowed_time = models.IntegerField(u'交易时间段',default=7,blank=True,null=True)
    allowed_card = models.IntegerField(u'交易可允许卡别',default=15,blank=True,null=True)
    allowed_currency = models.IntegerField(u'交易可使用币种',default=3,blank=True,null=True)
    allowed_amount_dc = models.IntegerField(u'借记卡单笔上限',default=500000,blank=True,null=True)
    allowed_amount_cc = models.IntegerField(u'信用卡单笔上限',default=500000,blank=True,null=True)
    
    is_developer = models.IntegerField(u'是否是开发者',default=1,choices=IS_DEVELOPER_CHOICES)
    last_modify = models.DateField(u'最后变更时间',auto_now_add=True)
    last_admin = models.IntegerField(u'最后变更人ID')
    
    class Meta:
        db_table = 'profile'
        
    def display_userid(self):
        return self.user.id
    display_userid.short_description = 'userid'

class Invoice(models.Model):
    ORDERFORMTYPE_CHOICE = (
        (1,'渠道'),
        (2,'直营'),
        (3,'内部'),
    )

    BUYTYPE_CHOICE = (
        (2,'货到付款'),
        (1,'在线支付'),
        (3,'渠道支付'),
    )

    AUDITSTATE_CHOICE = (
        (1,'待审批'),
        (2,'直营自动审批通过'),
        (3,'审批通过'),
        (4,'审核失败'),
    )
    
    PAYSTATE_CHOICE = (
        (1,'未支付'),
        (2,'已支付'),
    )

    id = models.AutoField(primary_key=True)
    orderid = models.CharField(u'订单号',max_length=32,blank = True,null = True)
    orderformtype = models.SmallIntegerField(u'订单类型',default=1,choices=ORDERFORMTYPE_CHOICE)
    buyerid = models.IntegerField(u'购买人ID')
    buyername = models.CharField(u'购买人姓名',max_length=16)
    buyercontactmethod = models.CharField(u'购买人联系方式',max_length=16)
    buyeraddress = models.CharField(u'购买人配送地址',max_length=256)
    buytype = models.SmallIntegerField(u'购买方式',choices = BUYTYPE_CHOICE)
    paymoney = models.IntegerField(u'付款金额')
    terminalcount = models.IntegerField(u'购买读卡器数量')
    paystate = models.SmallIntegerField(u'支付状态',choices = PAYSTATE_CHOICE)
    former = models.CharField(u'制单人',max_length=16)
    producetime = models.DateTimeField(u'下单时间')
    auditstate = models.SmallIntegerField(u'审批状态',choices = AUDITSTATE_CHOICE)
    auditer = models.CharField(u'审批人',max_length=16,default = '',blank=True,null=True)
    class Meta:
        db_table = 'invoice'
        verbose_name_plural = u'发货单'
    

class ChannelUser(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.IntegerField(u'用户ID')
    chnlid = models.IntegerField(u'渠道ID',default=3)
    chnluserid = models.CharField(u'渠道分配用户名',max_length=16,default='821110153000000')
    chnltermid = models.CharField(u'渠道终端号',max_length=20,default='00000000')
    last_modify = models.DateTimeField('最后修改时间',blank=True,auto_now_add=True)
    chnlusernm = models.CharField(u'渠道分配用户名',max_length=256,blank=True,default='北京钱方银通')
    mcc = models.CharField('渠道给钱方分配的商户类型',max_length=4, blank=True,default='5998')
    class Meta:
        db_table = 'chnluser'
        #app_label= u'usermanager'
        verbose_name_plural = u'支付渠道绑定'

class Recharge(models.Model):
    id = models.AutoField(primary_key=True) #订单号
    userid = models.CharField(u'用户ID',max_length=64) #钱方的用户id
    type=models.SmallIntegerField(u'订单类型') #订单类型 1表示支付押金；2表示货到付款,3渠道支付
    desc=models.CharField(u'配送地址',max_length=100) #配送地址
    fee = models.FloatField(u'交易金额') #交易金额
    sucesstime = models.DateTimeField(u'支付宝账号成功时刻',auto_now = True) #支付宝账号成功时刻
    buyer = models.CharField(u'购买账号',max_length=30) #买家的支付宝账号或者手机号
    buyerid = models.CharField(u'编号',max_length=30) #买家支付宝账号
    status = models.SmallIntegerField(u'付款状态') #付款状态  0表示未支付成功；1表示支付成功
    class Meta:
        db_table='charge'
        #app_label = 'usermanager'
        verbose_name = u'购买记录'
        db_tablespace=u'mis'
        verbose_name_plural = u'读卡器购买记录'
    
    def transformat_sucesstime(self):
        return self.sucesstime.date()

    transformat_sucesstime.short_description='支付宝账号成功时刻'
    transformat_sucesstime.admin_order_field='sucesstime'
    def display_type(self):
        if self.type == 1:
            return u'押金'
        elif self.type == 2:
            return u'货到付款'
        elif self.type == 3:
            return u'神码渠道支付'
        else:
            return u'----'
    display_type.short_description = u'支付类型'
    display_type.admin_order_field = 'type'
    
    def display_status(self):
        if self.status == 0:
            return u'未支付'
        elif self.status == 1:
            return u'支付成功'
        else:
            return u'---'
    display_status.short_description = u'支付状态'
    display_status.admin_order_field = 'status'

#some proxy for user/person/sperson/merchant
class UserProxy(User):
    '''
    UserProxy
    '''
    class Meta:
        proxy = True
   
    def set_trade_limit(self,deposit_amount,credit_amount):
        '''
        设置交易限额
        借记卡限额，信用卡限额
        '''
        p = self.get_xuser()
        allowed_amount=int(deposit_amount)<<16|int(credit_amount)
        p.allowed_amount = allowed_amount
        p.save()
            

    def bind_to_channel(self,channel_name,mcc):
        '''
        绑定交易渠道
        '''
        #import pdb
        #pdb.set_trace()
        CHANNEL = {u'北京钱方银通':{'chnluserid':'821110153000000','chnltermid':'00000000'},
                   u'北京智网宇通':{'chnluserid':'821110173990001','chnltermid':'00010001'}}
        if ChannelUser.objects.filter(userid = self.id).count() >  0:
            ChannelUser.objects.filter(userid = self.id).update(
                chnlusernm = channel_name,
                mcc = mcc,
                chnluserid = CHANNEL.get(channel_name,{}).get('chnluserid','821110153000000'),
                chnltermid = CHANNEL.get(channel_name,{}).get('chnltermid','00000000'),
            )
        else:
            sa = ChannelUser(userid = self.id,
                             chnlusernm = channel_name,
                             mcc = mcc,
                             chnluserid = CHANNEL.get(channel_name,{}).get('chnluserid','821110153000000'),
                             chnltermid = CHANNEL.get(channel_name,{}).get('chnltermid','00000000'),
)
            sa.save()
    
    def set_amount_limit(self,deposit_rate,credit_rate,amount):
        '''
        设置手续费settle.account
        '''
        if Account.objects.filter(userid = self.id).count()>0:
            Account.objects.filter(userid = self.id).update(
                feeratio = float(deposit_rate)/100,
                creditratio = float(credit_rate)/100,
                maxfee = int(amount),
            )
        else:
            from audit.models import Apply
            ac = Apply.objects.filter(user = self.id)
            if ac.count()>0:
                sa=Account(userid = self.id,
                        feeratio = float(deposit_rate)/100,
                        creditratio = float(credit_rate)/100,
                        maxfee = int(amount),
                        stayinterval = 1,
                        srcid =ac[0].groupid,
                        income = 0,
                        settlecount = 0,
                        settlenum = 0,
                        remaining = 0,
                )
                sa.save()
            else:
                pass

    def get_xuser(self):
        '''
        获取用户的详细信息P/SP/M
        '''
        if self.user_type == UserType.PERSON:
            return PersonProxy.objects.get(user=self)
        elif self.user_type == UserType.SPERSON:
            return SPersonProxy.objects.get(user=self)
        elif self.user_type == UserType.MERCHANT:
            return MerchantProxy.objects.get(user=self)
        else:
            raise Exception('user_type not found!userid:%s,user_type:%s' % (self.pk,self.user_type))

    def get_type_desc(self,type=None):
        '''
        商户类型
        '''
        if type is None:
            type = self.user_type

        return  UserType.get_type_desc(type)

    def get_level_desc(self,level=None):
        '''
        级别
        '''
        if level is None:
            level = self.user_level    
        
        return AccountType.get_type_desc(level)
        

    def get_source_desc(self):
        '''
        申请方式
        '''
        try:
            return Apply.objects.get(user__id=self.pk).src
        except:
            return u'网站注册'
    
    def get_state_desc(self):
        '''
        用户状态
        '''
        return UserState.get_type_desc(self.state) 
    
    def get_terminal_count(self):
        '''
        读卡器数量
        '''
        try:
            return TerminalBind.objects.valus('user','terminalid').\
                                            filter(user__id=self.pk).count()
        except:
            return 0
      
    def create_profile(self,apply,admin_id):

        user = User.objects.get(id=apply.user)
        if apply.state in [ApplyState.WAIT_AUDIT,ApplyState.WAIT_REAUDIT]:
            if apply.mcc is None:
                apply.mcc = '5988'
            if user.user_type == UserType.PERSON:
                person = Person.objects.filter(user=user)
                person = person.count() > 0 and person[0] or Person()
                
                person.user = user
                person.username=apply.name
                person.post = apply.post
                person.id_number = apply.idnumber
                person.address = apply.businessaddr 
                person.mobile = user.mobile
                person.edu = 1
                person.bank_name= apply.bankname 
                person.bank_account = apply.bankaccount
                person.bankuser = apply.bankuser
                person.last_admin = admin_id
                person.nickname = apply.nickname
                person.city = apply.city
                
                person.save()
                profile_pk = person.pk
            elif user.user_type == UserType.SPERSON:
                sperson = SPerson.objects.filter(user=user)
                sperson = sperson.count() > 0 and sperson[0] or SPerson() 
                
                sperson.user = user
                sperson.company = apply.name
                sperson.id_number = apply.idnumber
                sperson.business_addr = apply.businessaddr
                sperson.legal_person = apply.legalperson
                sperson.post = apply.post
                sperson.telephone = apply.telephone
                sperson.bankname = apply.bankname
                sperson.bankaccount = apply.bankaccount
                sperson.bankuser = apply.bankuser
                sperson.license_number = apply.licensenumber
                sperson.license_end_date = apply.licenseend_date
                sperson.contact = apply.contact
                sperson.last_admin = admin_id
                sperson.mobile = user.mobile
                sperson.nickname = apply.nickname
                sperson.city = apply.city
                
                sperson.save()
                profile_pk = sperson.pk
            elif user.user_type == UserType.MERCHANT:
                merchant = Merchant.objects.filter(user=user)
                merchant = merchant.count() > 0 and merchant[0] or Merchant() 
               
                merchant.user = user
                merchant.company = apply.name
                merchant.legal_person = apply.legalperson
                merchant.id_number = apply.idnumber
                merchant.license_number = apply.licensenumber
                merchant.licence_end_date = apply.licenseend_date
                merchant.post = apply.post
                merchant.business_addr = apply.businessaddr
                merchant.contact = apply.contact
                merchant.telephone = apply.telephone
                merchant.mobile = user.mobile
                merchant.bankname = apply.bankname
                merchant.bankaccount = apply.bankaccount
                merchant.bankuser = apply.bankuser
                merchant.last_admin = admin_id
                merchant.nickname = apply.nickname
                merchant.city = apply.city 
                
                merchant.save()
                profile_pk = merchant.pk
            else:
                pass

            #将apply表中数据插入到profile中
            #import pdb
            #pdb.set_trace()
            try:
                profile = Profile.objects.filter(user=user)
                profile = profile.count() > 0 and profile[0] or Profile()
    
                profile.user = user
                profile.nickname = apply.nickname
                profile.type = apply.usertype
                profile.provision = apply.provision
                profile.province = apply.province
                profile.city = apply.city
                profile.terminalcount = str(apply.terminalcount)
                profile.banktype = apply.banktype
                profile.bankname= apply.bankname 
                profile.bankaccount = apply.bankaccount
                profile.bankuser = apply.bankuser
                profile.mobile = user.mobile
                profile.allowarea = int(apply.allowarea or '0')
                profile.businessaddr = apply.businessaddr
                profile.address = apply.address
                profile.post = apply.post
                profile.telephone = apply.telephone
                profile.email = apply.email
                profile.area = apply.area
                profile.logisticaddr = apply.logisticaddr
                profile.tid = apply.tid
                profile.mcc = apply.mcc
                profile.orgcode = apply.orgcode
                profile.last_admin = admin_id
                profile.longitude = apply.longitude
                profile.latitude = apply.latitude
                profile.memo = apply.ext
    
                profile.name = apply.name
                profile.idnumber = apply.idnumber
                profile.idenddate = apply.idenddate
    
                profile.needauth = apply.needauth
                profile.licensenumber = apply.licensenumber
                profile.legalperson = apply.legalperson
                profile.licenseend_date = apply.licenseend_date
                profile.taxnumber = apply.taxnumber
                profile.contact = apply.contact
                profile.passcheck = apply.passcheck
                profile.founddate = apply.founddate
                profile.groupid = apply.groupid
    
                profile.save()
                #profile_pk = profile.pk
            except:
                pass

        if profile_pk > 0:
            apply.state = ApplyState.PASSED
            apply.save()
            user.state = 2
            user.save()
        
        return profile_pk

class PersonProxy(Person):
    '''
    '''
    class Meta:
        proxy = True

    def user(self):
        user_proxy = UserProxy()
        user_proxy.__dict__ = super(PersonProxy,self).user.__dict__
        return user_proxy

class SPersonProxy(SPerson):
    '''
    '''
    class Meta:
        proxy = True

    def user(self):
        user_proxy = UserProxy()
        user_proxy.__dict__ = super(SPersonProxy,self).user.__dict__
        return user_proxy

class MerchantProxy(Merchant):
    '''
    '''
    class Meta:
        proxy = True

    def user(self):
        user_proxy = UserProxy()
        user_proxy.__dict__ = super(MerchantProxy,self).user.__dict__
        return user_proxy


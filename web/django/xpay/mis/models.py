#!/usr/bin/env python
#coding=utf-8
# Copyright 2011
# Author fengyong@qfpay.net
import pickle,pdb,types,logging
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.core import serializers
from django.template.loader import render_to_string
from django.utils import simplejson
from util import fields

from util.define import *
from util.fields import ForeignKeyAcrossDB
from datetime import datetime
from audit.models import Upgrade as _up,UpgradeVoucher as _upVoucher

from util.sendsms import sendsms,sendmail
#from qfpay import MIS_NOTIFY

_log = logging.getLogger('mis_info')

class Psam(models.Model):
    PSAM_USED_CHOICES = (
        (0,u'入库'),
        (1,'已分配'),
        (2,u'出库'),
    )

    PSAM_STATUS_CHOICES = (
        (0,u'正常'),
        (1,u'已维修'),
        (2,u'报废'),
    )

    PSAM_TYPE_CHOICES = (
        ('21',u'钱方3des'),
        ('22',u'富友3des'),
    )
    
    PSAM_PRODUCER_CHOICES=(
        ('0001',u'艾创'),
    )
    
    PSAM_MODEL_CHOICES=(
        ('0001',u'psam'),
    )
    
    id = models.AutoField(primary_key=True)
    psamid = models.CharField(u'PSAM卡号',max_length=8,unique=True)
    psamtp = models.CharField(u'PSAM卡类型',max_length=2,choices=PSAM_TYPE_CHOICES)
    terminalid = models.CharField(u'设备编号',max_length=20,null=True,blank=True)
    producer = models.CharField(u'生产厂商',max_length=4,choices=PSAM_PRODUCER_CHOICES)
    model = models.CharField(u'PSAM卡型号',max_length=4,choices=PSAM_MODEL_CHOICES)
    produce_date = models.DateTimeField(u'生产日期')
    pinkey1 = models.CharField(u'解密因子（PIN母密钥1）',max_length=32)
    pinkey2 = models.CharField(u'解密因子（PIN母密钥2）',max_length=32)
    mackey = models.CharField(u'解密因子（MAC母密钥）',max_length=32)
    diskey = models.CharField(u'解密因子（BANKID）',max_length=32)
    used = models.SmallIntegerField(u'使用状态',choices=PSAM_USED_CHOICES)
    state = models.SmallIntegerField(u'状态',choices=PSAM_STATUS_CHOICES)
    last_modify = models.DateTimeField(u'最后变更时间',auto_now=True)
    last_admin = models.IntegerField(u'最后变更人ID')
    advice = models.CharField(u'建议',max_length=256,blank=True,null=True)
    class Meta:
        db_table = 'psam'
        app_label= u'mis'
        verbose_name_plural = u'PSAM卡管理'

class Terminal(models.Model):
    TERMINAL_USED_CHOICES = (
        (0,u'入库'),
        (1,u'已分配PSAM卡'),
        (2,u'已分配用户'),
        (3,u'发货中'),
        (4,u'发货成功'),
    )

    TERMINAL_STATUS_CHOICES =(
        (0,u'正常'),
        (1,u'维修中'),
        (2,u'报废'),
    )
    
    TERMINAL_PRODUCER_CHOICES=(
        ('0001',u'艾创'),
        ('0002',u'鼎合'),
    )

    TERMINAL_MODEL_CHOICES=(
        ('0001',u'qpos'),
        ('0002',u'ipos'),
    )
    
    GROUP_CHOICES = (
        (10002,u'山东银晟昌'),
        (0,u'钱方'),
    )

    id = models.AutoField(u'终端ID',primary_key=True)
    user = ForeignKeyAcrossDB(User,db_column="userid",verbose_name=u'用户ID',default=0)
    terminalid = models.CharField(u'设备编号',max_length=20,unique=True)
    psamid = models.CharField(u'PSAM编号',max_length=8)
    producer = models.CharField(u'生产厂商',max_length=4,choices =TERMINAL_PRODUCER_CHOICES)
    model = models.CharField(u'设备型号',max_length=4,choices =TERMINAL_MODEL_CHOICES)
    produce_date = models.DateTimeField(u'生产日期')
    deliver_date = models.DateTimeField(u'发放日期',blank=True,null=True)
    tck = models.CharField(u'TCK密文',max_length=32)
    used = models.SmallIntegerField(u'使用状态',choices = TERMINAL_USED_CHOICES,default=0)
    state = models.SmallIntegerField(u'状态',choices = TERMINAL_STATUS_CHOICES,default=0)
    last_modify = models.DateTimeField(u'最后变更时间',auto_now=True)
    last_admin = models.IntegerField(u'最后变更人ID',default=0)
    advice = models.CharField(u'建议',max_length=256,null=True,default=u'')
    group_id = models.IntegerField(u'渠道ID',default=0,null=True,blank=True,choices=GROUP_CHOICES)

    class Meta:
        db_table = 'terminal'
        app_label= u'mis'
        verbose_name_plural = u'读卡器管理'

class VoucherInfoManager(models.Manager):
    def get_a_voucher(self,user_id=None,license_type=None):
        if user_id is None or license_type is None:
            raise Exception('argument not match exception!')

        #pdb.set_trace()
        v = list(super(type(self),self).get_query_set().filter(user_id=user_id,license_type=license_type))
        if len(v)==1 and v[0].content:
            return simplejson.loads(v[0].content)[0]         
        else:
            raise Exception(u'voucher not inputed!VoucherInfoManager.get_a_voucher not exists userid = %s vouchertype = %s' % (user_id,license_type))

class VoucherDataInfo(models.Model):
    '''
    凭证信息表-各种证件录入完毕后会统一保存到此表内
    content格式为各证件pickle.dumps的字符串信息
    '''
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    license_type = models.IntegerField()
    content = models.CharField(max_length=4096)
    content_method = models.CharField(max_length=24,default='json') #序列化方法，默认'json'
    create_user = models.IntegerField()
    create_date = models.DateTimeField(auto_now_add=True)
    state = models.SmallIntegerField(default=0)
    is_delete = models.BooleanField(default=0)

    objects = VoucherInfoManager()
    
    class Meta:
        db_table = 'mis_voucherinfo'

class VoucherManager(models.Model):
    def save(self,*args,**kwargs):
        if (kwargs['__owner'] is None 
        or kwargs['__type'] is None
        or kwargs['__currentUser'] is None
        or kwargs['__level'] is None
        or kwargs['__upid'] is None):
            raise Exception('content or operator is null!!')
        
        #pdb.set_trace()
        voucher = VoucherDataInfo.objects.filter(user_id = kwargs['__owner'],license_type=kwargs['__type'])[0:1]
        if len(voucher) == 0:
            voucher = VoucherDataInfo() 
        else:
            voucher = voucher[0]

        voucher.user_id = kwargs['__owner']
        voucher.license_type = kwargs['__type']
        voucher.content = serializers.serialize('json',[self,]) #pickle.dumps(self)
        voucher.content_method = 'json'
        voucher.create_user = kwargs['__currentUser'].id
        voucher.state = 0
        voucher.is_delete = 0

        voucher.save()

        if voucher.id is not None and voucher.id > 0:
            upinfo =_up.objects.get(pk=kwargs['__upid'])
            #pdb.set_trace()
            _upVoucher.objects.filter(upgrade_id=upinfo,
                                      cert_type=voucher.license_type)\
                              .update(input_state = 1,
                                      typist_user = kwargs['__currentUser'].id,
                                      typist_time = datetime.now())
            upVoucherList = _upVoucher.objects.filter(upgrade_id=upinfo,\
                                                      input_state=1)
            user = User.objects.get(pk=upinfo.user_id)
            if len(upVoucherList) == UPGRADE_IMAGE.UPGRADE_COUNT_FOR_UPGRADE.get('USER_TYPE_'+str(user.user_type),0):
                upinfo.input_state = 1
                upinfo.save()

class IDCardInfo(VoucherManager):
    '''
    凭证信息-身份证
    '''
    name = models.CharField(max_length=30)
    gender = models.SmallIntegerField()
    nation = models.CharField(max_length=64)
    address = models.CharField(max_length=128)
    idNumber = models.CharField(max_length=20)
    grant_org = models.CharField(max_length=64)
    start_date = models.DateField()
    end_date = models.DateField()

    def save(self,*args,**kwargs):
        '''
        需要两个参数owner和currentUser(request.user)
        '''
        kwargs['__type'] = LICENSE_TYPE.ID_CARD 
        super(IDCardInfo,self).save(*args,**kwargs)

class TaxInfo(VoucherManager):
    '''
    凭证信息-税务登记证
    '''
    number = models.CharField(max_length=30)
    name = models.CharField(max_length=64)
    legal_person = models.CharField(max_length=64)
    reg_type = models.CharField(max_length=128)
    scope = models.CharField(max_length=20)
    approved_org = models.CharField(max_length=64)
    obligation = models.CharField(max_length=64)
    approved_date = models.DateField(auto_now_add=True)

    def save(self,*args,**kwargs):
        '''
        需要两个参数owner和currentUser(request.user)
        '''
        kwargs['__type'] = LICENSE_TYPE.TAX 
        super(TaxInfo,self).save(*args,**kwargs)
        
class ContractInfo(VoucherManager):
    '''
    凭证信息-房屋租赁合同
    '''
    lessor = models.CharField(max_length=30)
    lessee = models.CharField(max_length=30)
    start_date = models.CharField(max_length=64)
    end_date = models.DateField()
    address = models.CharField(max_length=256)

    def save(self,*args,**kwargs):
        '''
        需要两个参数owner和currentUser(request.user)
        '''
        kwargs['__type'] = LICENSE_TYPE.CONTRACT
        super(ContractInfo,self).save(*args,**kwargs)

class OrgcodeInfo(VoucherManager):
    '''
    凭证信息-组织结构代码证
    '''
    orgcode = models.CharField(max_length=20)
    name = models.CharField(max_length=256)
    type = models.CharField(max_length=128)
    address = models.CharField(max_length=256)
    start_date = models.DateField()
    end_date = models.DateField()
    grant_org = models.CharField(max_length=20)
    number = models.CharField(max_length=64)

    def save(self,*args,**kwargs):
        '''
        需要两个参数owner和currentUser(request.user)
        '''
        kwargs['__type'] = LICENSE_TYPE.ORG_CODE 
        super(OrgcodeInfo,self).save(*args,**kwargs)

class LicenseInfo(VoucherManager):
    '''
    凭证信息-营业执照
    '''
    number = models.CharField(max_length=30)
    name = models.CharField(max_length=32)
    address = models.CharField(max_length=256)
    legal_person = models.CharField(max_length=32)
    type = models.CharField(max_length=20)
    scope = models.CharField(max_length=64)
    reg_captail = models.CharField(max_length=64)
    rel_income = models.CharField(max_length=64)
    found_date = models.DateField(auto_now_add=True)
    lc_end_date = models.DateField(auto_now_add=True)
    approved_date = models.DateField(auto_now_add=True)
    
    def save(self,*args,**kwargs):
        '''
        需要两个参数owner和currentUser(request.user)
        '''
        kwargs['__type'] = LICENSE_TYPE.LICENSE 
        super(LicenseInfo,self).save(*args,**kwargs)
class OpLogManager(models.Manager):
    def log_action(self,admin_id,op_type,action=' ',detail=' ',memo=' ',notify_type=0):
        '''
        @admin_id = 管理员ID
        @op_type = [1,2,3,4] 
        @action = 业务操作 eg：审核通过、审核失败、加入黑名单,
        @detail = 详情,
        @memo = 备注,
        @notify_type = [0,1,2] 0不通知，1邮件，2短信，3邮件&短信
        @return None
        '''
        log = self.model(admin_id = admin_id,
                        op_type = op_type,
                        action = action,
                        detail = detail,
                        memo = memo,
                        notify_type = notify_type)
        log.save() 
        try:
            import threading
            t = threading.Thread(target=OpLogManager.notify,args=(self,log))
            t.start()
            #self.notify(log)
        except Exception,ex:
            _log.exception(ex)
    
    def notify(self,logObj):
        content = logObj.detail
        if type(logObj.detail) == types.UnicodeType:
            content = content.encode('utf-8')
 
        msg = '管理员:{0},操作详情:{1}'.format(logObj.admin_id,content)
        if logObj.notify_type in [1,3]:
            self._notify_email(msg)

        if logObj.notify_type in [2,3]:
            self._notify_sms(msg)

    def _notify_email(self,msg):
        toList = MIS_NOTIFY.get('MAIL',[])
        if len(toList) > 0:
            sendmail(toList,u'管理后台管理员操作提醒邮件',msg)

    def _notify_sms(self,msg):
        for mobile in MIS_NOTIFY.get('MOBILE',[]):
            if mobile and isinstance(mobile,int) and len(str(mobile)) == 11:
                sendsms(mobile,msg)

class OpLog(models.Model):
    '''记录所有管理员的业务操作'''
    CHOICES_OP_TYPE = (
        (1,u'审核系统'),
        (2,u'交易系统'),
        (3,u'风控系统'),
        (4,u'设备管理'),
    )
    CHOINCES_NOTIFY_TYPE = (
        (0,u'不通知'),
        (1,u'邮件'),
        (2,u'短信'),
        (3,u'邮件&短信'),
    )
    id = models.AutoField(primary_key=True)
    admin_id = fields.ForeignKeyAcrossDB(User,verbose_name=u'管理员Id')
    op_type = models.IntegerField(u'业务类型',choices=CHOICES_OP_TYPE)
    action = models.CharField(u'业务操作',blank=False,null=False,max_length=128)
    detail = models.TextField(u'操作详情', blank=False,null=False)
    memo = models.TextField(u'备注',blank=True,null=True)
    notify_type = models.IntegerField(u'通知方式',blank=False,default=0,choices=CHOINCES_NOTIFY_TYPE)
    action_time = models.DateTimeField(u'操作时间', auto_now=True)
    
    objects = OpLogManager()

    class Meta:
        db_table = 'mis_oplog'
        verbose_name = u'管理员操作日志'
        verbose_name_plural = u'管理员操作日志'

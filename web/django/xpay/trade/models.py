#!/usr/bin/env python
#coding=utf-8
# Copyright 2011
# Author fengyong@qfpay.net
import datetime,time
from django.db import models
from django.contrib.auth.models import User
from core.models import Person,SPerson,Merchant
from risk.models import BUSICD_CHOICES
# Create your models here.
class RecordManager(models.Manager):

    def gen_sql(self,table, userid, start, end, status, sn, card, sum,include_cancel=False):
        '''根据查询条件构造出SQL语句'''
        format = "%Y-%m-%d %H:%M:%S"
        if not userid:
            sql = 'select * from %s where  (busicd="000000" or busicd="200000" or busicd="201000") and status=1 and sign=1 ' %(table)
        else:
            sql = 'select * from %s where userid=%d and (busicd="000000" or  busicd="200000" or busicd="201000") and status=1 and sign=1 ' %(table,userid)

        if not include_cancel:
            sql += ' and cancel!=1 '
            

        #根据时间查询
        if start != '' and end != '':                 
            d1 = datetime.datetime(*time.strptime(start,format)[:6])
            d2 = datetime.datetime(*time.strptime(end, format)[:6])
            sysdtm = ' and (sysdtm between "%s" and  "%s") ' %(d1,d2)
            sql += sysdtm
        
        '''
        #根据交易状态查询
        if status == u'交易成功':
            state = ' and (status=1) '
            sql += state
        elif status == u'交易失败':
            state = ' and (status=2 or status=3) '
            sql += state
        '''
        #根据交易流水号查询
        if sn != '':
            serial = " and (syssn = '%s') " %sn
            sql += serial

        #根据卡号进行查询
        if card != '':
            cardno = ' and (cardcd = "%s") ' %card
            sql += cardno

        #根据交易金额进行查询
        if sum>0:
            mny = ' and (txamt = %d) ' %sum
            sql += mny
        
        sql += ' order by sysdtm desc'
        return sql

    def get_by_syssn(self, userid, sn,include_cancel=True):
        '''根据交易流水号查询交易记录'''
        table = 'record_'+sn[:8]
        sql = self.gen_sql(table, userid, '','','',sn,'',0,include_cancel=include_cancel)
        qs = Record.objects.raw(sql)
        result = None
        for p in qs:
            result = p
            break

        return result

    def get_all_results(self,userid,start,end,status,sn,card,sum):
        '''取出所有交易流水表的结果'''
        format = "%Y-%m-%d %H:%M:%S"
        if start=='':
            start_date = datetime.datetime(2012,1,1)
        else:
            start_date = datetime.datetime(*time.strptime(start,format)[:6])

        if end=='':
            end_date = datetime.datetime.now()
        else:
            end_date = datetime.datetime(*time.strptime(end,format)[:6])
        days = (end_date-start_date).days
        
        qs = []
        for day in range(0,days+1):
            date = end_date-datetime.timedelta(day,0,0)
            table = 'record_' + date.strftime('%Y%m%d')
            sql = self.gen_sql(table, userid, start, end, status, sn, card, sum)
            try:
                day_qs = Record.objects.raw(sql)
                for record in day_qs:
                    qs.append(record)
            except:
                continue
        return qs

class Channel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(u'渠道名',max_length=32)
    zmk = models.CharField(u'渠道主密钥',max_length=36, blank=True)
    zpk = models.CharField(u'渠道工作密钥',max_length=36, blank=True)
    mcc = models.CharField(u'渠道给钱方分配的商户类型',max_length=4, blank=True)
    chcd = models.CharField(u'平台分配机构号',max_length=16, blank=True)
    inscd = models.CharField(u'接入路由分配机构号',max_length=16, blank=True)
    code = models.CharField(u'渠道代码',max_length=4, blank=True)
    regioncd = models.CharField(u'渠道地区代码',max_length=8, blank=True)
    mchntid = models.CharField(u'渠道给钱方分配的商户号',max_length=32, blank=True)
    mchntnm = models.CharField(u'渠道给钱方分配的商户名',max_length=32, blank=True)
    terminalid = models.CharField(u'渠道给钱方分配的终端号',max_length=32, blank=True)
    mode = models.SmallIntegerField(u'渠道接入方式',blank=True, default=0)
    class Meta:
        db_table = 'channel'
        #app_label= u'trade'
        db_tablespace = u'core'
        verbose_name_plural = u'支付渠道'
    
class Record(models.Model):
    CARD_TYPE_CHOICES = (
        ('01','借记卡'),
        ('02','信用卡'),
        ('03','储值卡'),
    )

#    BUSS_TYPE_CHOICES = (
#        ('000000','交易消费'),
#        ('400000','卡卡转账'),
#        ('210000','还信用卡'),
#        ('300000','查询余额'),
#        ('200000','退货交易'),
#        ('201000','消费撤销'),
#        ('041000','撤销冲正'),
#        ('040000','消费冲正'),
#        ('180100','存根上传'),
#        ('180200','交易列表'),
#    )

    TRADE_STATE_CHOICES = (
        (0,'交易中'),
        (1,'交易成功'),
        (2,'交易失败'),
        (3,'交易超时'),
    )

    TRADE_CANCEL_CHOCES = (
        (0,'无'),
        (1,'已冲正'),
        (2,'已撤销'),
        (3,'已退货'),
    )
    SIGN_CHOICES = (
        (0,u'无签名'),
        (1,u'有签名'),
    )
    busicd = models.CharField(u'业务类型',max_length=6,choices=BUSICD_CHOICES) #业务代码
    userid = models.IntegerField(u'商户ID')
    psamid = models.CharField(u'PSAM卡号',max_length=8)
    udid = models.CharField(u'手机编号',max_length=40)
    cardtp = models.CharField(u'卡类型',max_length=2,choices = CARD_TYPE_CHOICES)
    cardcd = models.CharField(u'卡号',max_length=19)
    txamt = models.IntegerField(u'交易额')#单位分
    txcurrcd = models.CharField(u'币种',max_length=3)
    clisn = models.CharField(u'客户端流水号',max_length=6)
    syssn = models.CharField(u'交易查询号',max_length=14)
    txdtm = models.DateTimeField(u'客户端交易时间')
    txzone = models.CharField(u'交易时区',max_length=5)
    chnltm = models.DateField(u'清算时间')
    busichnl = models.CharField(u'POS类型',max_length=3)
    posentrymode = models.CharField(u'pos输入码',max_length=3)#输入点方式021/022
    debitacntname = models.CharField(u'借记卡账户名',max_length=64)
    debitacntbank = models.CharField(u'借记卡开户行',max_length=64)
    debitacntcd = models.CharField(u'借记卡卡号',max_length=19)
    creditacntcd = models.CharField(u'信用卡卡号',max_length=19)
    regioncd = models.CharField(u'交易方地区码',max_length=4)
    custmrtp = models.CharField(u'客户账号类型',max_length=4)
    custmrno = models.CharField(u'客户账号',max_length=20)#客户端帐号
    custmrpin = models.CharField(u'客户密码',max_length=40)
    custmrpinfmt = models.CharField(u'客户密码加密格式',max_length=2)
    orderno = models.CharField(u'订单号',max_length=40)
    origssn = models.CharField(u'原交易查询号',max_length=14)
    origbusicd = models.CharField(u'原业务代码',max_length=6)
    origdtm = models.DateTimeField(u'原交易时间')
    longitude = models.FloatField(u'经度')
    latitude = models.FloatField(u'纬度')
    chnlid = models.CharField(u'渠道代码',max_length=4)
    authid = models.CharField(u'授权号',max_length=6)
    retcd = models.CharField(u'返回码',max_length=4)
    status = models.SmallIntegerField(u'状态',choices=TRADE_STATE_CHOICES)
    cancel = models.SmallIntegerField(u'取消',choices=TRADE_CANCEL_CHOCES)
    sysdtm = models.DateTimeField(u'交易时间')
    contact = models.CharField(u'收据发送地址',max_length=128,null=True)
    settlecd = models.SmallIntegerField(u'清算号')
    settletm = models.DateTimeField(u'清算时间')
    issuerbank = models.CharField(u'发卡行',max_length=32)
    sign = models.SmallIntegerField(u'签名',choices=SIGN_CHOICES)
    terminalid = models.CharField(u'读卡器ID',max_length=20)

    objects = RecordManager()
    class Meta:
        app_label=u'trade'
        verbose_name_plural = u'交易查询'
     
    def display_txamt(self):
        import locale
        d = self.txamt/100.00
        locale.setlocale(locale.LC_ALL,'')
        return locale.format("%.2f",d,1)
    display_txamt.short_description = u'交易额'

    def display_username(self):
        u = User.objects.get(pk=self.userid)
        if u.user_type == 1:
            p = Person.objects.get(user=u)
            return p.username
        elif u.user_type == 2:
            p = SPerson.objects.get(user=u)
            return p.company
        elif u.user_type == 3:
            p = Merchant.objects.get(user=u)
            return p.company
        return u.username
    display_username.short_description = u'商户名'

    def display_usermobile(self):
        try:
            u = User.objects.get(pk=self.userid)
            return u.username
        except:
            return u'-----'
    display_usermobile.short_description = u'手机号'
    display_usermobile.admin_order_field = 'userid'
    
    def display_contact(self):
        c = self.contact;
        if c is None or len(c) == 0:
            return u'未发送'
        else:
            return u'已发送'
    display_contact.short_description = u'收据'

    def display_contact_mail(self):
        c = self.contact
        if c is None or len(c) == 0:
            return '-'
        else:
            if c.find('@')>0:
                return '1'
            else:
                return '0'
    
    display_contact_mail.short_description = u'邮件'
    def display_contact_sms(self):
        is_mail = self.display_contact_mail()
        if is_mail == '1':
            return '0'
        elif is_mail == '0':
            return '1'
        else:
            return is_mail

    display_contact_sms.short_description = u'短信'

#!/usr/bin/env python
#coding=utf-8
# Copyright 2011
# Author fengyong@qfpay.net
from django.contrib.auth.models import User
from django.db import models

class Adjust(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.IntegerField(u'商户编号')
    adjust_type = models.SmallIntegerField(u'调账类型')
    adjust_num = models.IntegerField(u'调账金额')
    adjust_date = models.DateField(u'调账日期')
    adjust_state = models.SmallIntegerField(u'调账状态')
    operator = models.IntegerField()
    op_date = models.DateTimeField()
    op_demo = models.CharField(max_length=30)
    class Meta:
        db_table = 'adjust'
        db_tablespace = 'settle'
        verbose_name_plural = u'资金调账'

    def dis_adjustnum(self):
        return self.adjust_num/100.0
    dis_adjustnum.short_description = u'金额'

class Period(models.Model):
    id = models.AutoField(u'账期编号',primary_key=True)
    lastid=models.IntegerField(verbose_name='上一账期')
    start =models.DateField(u'账期起始日期')
    end = models.DateField(u'账期截止日期')
    operator = models.IntegerField(u'添加者')
    opdate = models.DateTimeField(u'添加日期')
    def __unicode__(self):
        return '%d' %(self.id)

    class Meta:
        db_table = 'account_period'
        db_tablespace = 'settle'
        verbose_name_plural = u'账期配置'

class Unequal(models.Model):
    STATE_CHOICES = ((0, u'待调账'),
    (1,u'已调帐'))

    id = models.AutoField(primary_key=True)
    userid = models.IntegerField(u'商户编号')
    errcode = models.IntegerField(u'错误代码')
    paychnl = models.IntegerField(u'支付渠道')
    merchantid = models.CharField(u'商户编号',max_length=20)
    tradetype = models.CharField(u'交易类型',max_length=10)
    refid= models.CharField(u'银联参考号',max_length=20)
    origdtm = models.DateTimeField(u'原交易时间')
    mcc = models.CharField(u'MCC',max_length=5)
    issuerbank = models.CharField(u'发卡行', max_length=50)
    currency = models.CharField(u'币种', max_length=5)
    cardcd = models.CharField(u'卡号',max_length=25)
    cardtp = models.SmallIntegerField(u'卡类型')
    tradenum = models.IntegerField(u'交易金额')
    tradedtm = models.DateTimeField(u'交易时间')
    tradefee = models.IntegerField(u'手续费')
    stldate = models.DateField(u'结算日期')
    syssn = models.CharField(u'流水号',max_length=15)
    terminalid = models.CharField(u'终端编号',max_length=20)
    chnlrtn = models.SmallIntegerField(u'渠道返回值')
    srcpid = models.IntegerField(u'结算账期')
    dstpid = models.IntegerField(u'调账账期')
    state = models.SmallIntegerField(u'调账状态', choices=STATE_CHOICES)
    auditor = models.IntegerField(u'审核员')
    auditdate = models.DateTimeField(u'审核时间', auto_now_add=True)
    auditdemo = models.CharField(u'备注',max_length=256)
    class Meta:
        db_table = 'unequal'
        db_tablespace = 'settle'
        verbose_name_plural = u'不平帐表'
    def display_tradenum(self):
        if not self.tradenum: self.tradenum = 0
        return self.tradenum/100.0
    display_tradenum.short_description = u'金额'

class Debit(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.IntegerField(u'商户编号')
    name = models.CharField(u'商户姓名',max_length=10)
    bankname = models.CharField(u'开户行', max_length=30)
    bankaccount = models.CharField(u'银行账号',max_length=30)
    payamt = models.IntegerField(u'打款金额')
    expectdate = models.DateField(u'打款日期')
    status = models.SmallIntegerField(u'打款状态')
    class Meta:
        db_table='debit'
        db_tablespace = 'settle'
        verbose_name_plural = u'划账表'
    def dis_payamt(self):
        return self.payamt/100.0
    dis_payamt.short_description = u'划账金额'

class Settle(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.IntegerField(u'商户编号')
    tradesum = models.IntegerField(u'交易总数')
    settlesum = models.IntegerField(u'结算金额')
    debitsum = models.IntegerField(u'打款金额')
    settlecnt = models.IntegerField(u'结算笔数')
    payfee = models.IntegerField(u'支付渠道手续费')
    qffee = models.IntegerField(u'钱方手续费')
    chnlfee = models.IntegerField(u'推广渠道手续费')
    adjust = models.IntegerField(u'调账金额')
    manual = models.IntegerField(u'手工调账')
    lastsettlesum = models.IntegerField(u'上期结算金额')
    lastdebitsum = models.IntegerField(u'上期打款金额')
    pid = models.ForeignKey('Period',db_column='pid')
    state = models.IntegerField(u'审核状态')
    class Meta:
        db_table='daily_settle'
        db_tablespace = 'settle'
        verbose_name_plural = u'商户每日结算明细'

    def xbill_date(self):
        str = self.pid.end.strftime('%Y%m%d')
        return '<a href="/admin/settle/settle/dlbill/?date=%s&userid=%d">%s</a>' %(str,self.userid,str)
    xbill_date.allow_tags = True
    xbill_date.short_description = u'下载账单'
    
    def pass_settle(self):
        return '<a href="/admin/settle/settle/pass/?date=%s&pid=%d">通过</a>' %(self.pid, self.userid)
    pass_settle.allow_tags = True
    pass_settle.short_description = u'审核通过'

    def dis_curperiod(self):    
        return self.pid.id
    dis_curperiod.short_description = u'本账期'

    def dis_curstart(self):
        return self.pid.start
    dis_curstart.short_description = u'起始日期'

    def dis_curend(self):
        return self.pid.end
    dis_curend.short_description = u'截止日期'

    def dis_tradenum(self):
        return self.tradesum/100.0
    dis_tradenum.short_description = u'交易金额'

    def dis_settlenum(self):
        return self.settlesum/100.0
    dis_settlenum.short_description= u'结算金额'

    def dis_payfee(self):
        return self.payfee/100.0
    dis_payfee.short_description = u'支付手续费'

    def dis_qffee(self):
        return self.qffee/100.0
    dis_qffee.short_description = u'钱方手续费'

    def dis_chnlfee(self):
        return self.chnlfee/100.0
    dis_chnlfee.short_description=u'渠道手续费'

    def dis_debit(self):
        return self.debitsum/100.0
    dis_debit.short_description = u'划账金额'

    def dis_adjust(self):
        return self.adjust/100.0
    dis_adjust.short_description = u'调帐金额'

    def dis_manual(self):
        return self.manual/100.0
    dis_manual.short_description = u'调整金额'

    def dis_lastsettle(self):
        return self.lastsettlesum/100.0
    dis_lastsettle.short_description = u'上期结算'

    def dis_lastdebit(self):
        return self.lastdebitsum/100.0
    dis_lastdebit.short_description = u'上期划账'

SETTLE_TYPE = ( (1,u'钱方结算'),
            (2,u'通联代结算'))

class SettleTrade(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.IntegerField(u'商户编号')
    groupid = models.IntegerField(u'推广渠道')
    chnlid = models.IntegerField(u'支付渠道')
    merchantid = models.CharField(u'支付商号', max_length=40)
    settletype = models.SmallIntegerField(u'结算类型', choices = SETTLE_TYPE)
    termid = models.CharField(u'终端编号',max_length=20)
    termsn = models.CharField(u'终端流水号', max_length=10)
    stldate = models.DateField(u'渠道结算日期')
    syssn = models.CharField(u'系统流水',max_length=20)
    mcc = models.CharField(u'行业编号', max_length=4)
    tradetype = models.CharField(u'交易类型', max_length=10)
    currency = models.SmallIntegerField(u'交易币种')
    tradedtm = models.DateTimeField(u'交易时间')
    cardtp = models.CharField(u'卡类型',max_length=5)
    cardcd = models.CharField(u'卡号', max_length=30)
    issuerbank = models.CharField(u'发卡行',max_length=50)
    origsyssn = models.CharField(u'原始交易号', max_length=20)
    origdtm = models.DateTimeField(u'原交易时间')
    tradenum = models.IntegerField(u'交易本金')
    settlenum = models.IntegerField(u'结算金额')
    payfee = models.IntegerField(u'支付渠道费用')
    qffee = models.IntegerField(u'钱方手续费')
    chnlfee = models.IntegerField(u'推广渠道手续费')
    class Meta:
        db_table='settle_20120506'
        db_tablespace = 'settle'
        verbose_name_plural = u'账期结算'
    def dis_tradenum(self):
        return self.tradenum/100.0
    dis_tradenum.short_description = u'交易金额'
    def dis_settlenum(self):
        if self.settlenum is None:
            return u'未结算'
        return self.settlenum/100.0
    dis_settlenum.short_description = u'结算金额'
    def dis_payfee(self):
        if self.payfee is None:
            return u'未结算'
        return self.payfee/100.0
    dis_payfee.short_description =u'支付渠道手续费'
    def dis_qffee(self):
        if self.qffee is None:
            return u'未结算'
        return self.qffee/100.0
    dis_qffee.short_description = u'钱方手续费'
    def dis_chnlfee(self):
        if self.chnlfee is None:
            return u'未结算'
        return self.chnlfee/100.0
    dis_chnlfee.short_description = u'推广渠道手续费'

class SettleStatis(models.Model):
    id = models.AutoField(primary_key=True)
    groupid = models.IntegerField(u'推广渠道')
    stldate = models.DateField(u'结算日期')
    usercnt = models.IntegerField(u'用户数')
    tradecnt = models.IntegerField(u'交易笔数')
    tradenum = models.IntegerField(u'交易本金')
    settlenum = models.IntegerField(u'结算金额')
    payfee= models.IntegerField(u'支付渠道费用')
    qffee= models.IntegerField(u'钱方手续费')
    chnlfee= models.IntegerField(u'推广渠道手续费')
    class Meta:
        db_table = 'settle_statis'
        db_tablespace = 'settle'
        verbose_name_plural = u'交易汇总'
    def dis_tradenum(self):
        return self.tradenum/100.0
    dis_tradenum.short_description = u'交易金额'
    def dis_settlenum(self):
        return self.settlenum/100.0
    dis_settlenum.short_description = u'结算金额'
    def dis_payfee(self):
        return self.payfee/100.0
    dis_payfee.short_description = u'支付渠道费'
    def dis_qffee(self):
        return self.qffee/100.0
    dis_qffee.short_description = u'钱方手续费'
    def dis_chnlfee(self):
        return self.chnlfee/100.0
    dis_chnlfee.short_description = u'推广渠道手续费'

class Account(models.Model):
    userid = models.IntegerField(u'商户编号',primary_key=True)
    srcid  = models.SmallIntegerField(u'推广渠道')
    feeratio = models.FloatField(u'储值卡费率')
    creditratio = models.FloatField(u'信用卡费率')
    maxfee = models.IntegerField(u'借记卡封顶',default=-1)
    creditmaxfee = models.IntegerField(u'信用卡封顶', default=-1)
    bankfee = models.CharField(u'银行费率配置', max_length=200)
    stayinterval = models.SmallIntegerField(u'到账时限')
    income = models.IntegerField(u'交易额')
    settlecount = models.IntegerField(u'交易笔数')
    settlenum = models.IntegerField(u'结算金额')
    remaining = models.IntegerField(u'账户余额')
    class Meta:
        db_table = 'account'
        db_tablespace = 'settle'
        verbose_name_plural = u'账户信息'
    def dis_interval(self):
        return 'T+'+`self.stayinterval`
    dis_interval.short_description=u'到账时限'

    def dis_settlenum(self):
        return self.settlenum/100.0
    dis_settlenum.short_description=u'结算金额'

    def dis_income(self):
        return self.income/100.0
    dis_income.short_description = u'营业额'

    def dis_remaining(self):
        return self.remaining/100.0
    dis_remaining.short_description = u'账户余额'


class Earning(models.Model):
    id = models.AutoField(primary_key=True)
    pid = models.ForeignKey(Period, db_column='pid')
    shouldpay = models.IntegerField(u'支付渠道应打款')
    realpay = models.IntegerField(u'支付渠道实际打款')
    payed = models.IntegerField(u'已打款')
    unpayed = models.IntegerField(u'未打款')
    qfearning = models.IntegerField(u'钱方收益')
    unequal = models.IntegerField(u'不平帐金额')
    
    def dis_pid(self):
        return self.pid.end.strftime('%Y-%m-%d')
    dis_pid.short_description = u'账期'

    def dis_should(self):
        return self.shouldpay/100.0
    dis_should.short_description = u'支付渠道应打款'
    def dis_realpay(self):
        return self.realpay/100.0
    dis_realpay.short_description=u'支付渠道实际打款'

    def dis_payed(self):
        return self.payed/100.0
    dis_payed.short_description = u'应打款'

    def dis_unpayed(self):
        return self.unpayed/100.0
    dis_unpayed.short_description = u'未打款'

    def dis_earning(self):
        return self.qfearning/100.0
    dis_earning.short_description = u'钱方收益'

    def dis_unequal(self):
        return self.unequal/100.0
    dis_unequal.short_description = u'不平帐款'

    class Meta:
        db_table = 'earning'
        db_tablespace = 'settle'
        verbose_name_plural = u'钱方收益'

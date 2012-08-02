#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from core.models import Person,SPerson,Merchant

import re
# Create your models here.
BUSICD_CHOICES = (
    ('000000',u'消费'),
    ('040000',u'消费冲正'),
    ('201000',u'消费撤销'),
    ('041000',u'消费撤销冲正'),
    ('200000',u'退货'),
    ('300000',u'余额查询'),
    ('180200',u'交易列表'),
    ('180100',u'签名上传'),
    ('032000',u'预授权'),
    ('042000',u'预授权冲正'),
    ('202000',u'预授权撤销'),
    ('044000',u'预授权撤销冲正'),
    ('033000',u'预授权完成'),
    ('043000',u'预授权完成冲正'),
    ('203000',u'预授权完成撤销'),
    ('045000',u'预授权完成撤销冲正'),
) 

RSTYPEID_CHOICES = (
    (1,'登录'),
    (2,'交易'),
)

def display_base(index):
    try:
        record = RiskCode.objects.get(code=index)
        return record.name
    except:
        return index

  
    
class Result(models.Model):
    rid = models.AutoField(primary_key=True)
    userid = models.IntegerField(u'商户ID')
    syssn = models.CharField(u'交易查询号',max_length=14)
    busicd = models.CharField(u'业务类型',max_length=6,choices=BUSICD_CHOICES)
    ckdate = models.DateTimeField(u'检查时间',null=True)
    ret = models.CharField(u'风控结果',max_length=8)
    rstype = models.IntegerField(u'风控类型',choices=RSTYPEID_CHOICES,blank=True)
    rstypeid = models.IntegerField(u'关联ID',blank=True)
    #success = models.SmallIntegerField(default=False)

    def display_ret(self):
        return display_base(self.ret)
    display_ret.short_description = u'风控结果'
    display_ret.admin_order_field = 'ret'

    def trans_ckdate(self):
        return self.ckdate
    trans_ckdate.allow_tags = True
    trans_ckdate.admin_order_field='ckdate'
    trans_ckdate.short_description=u'检查时间'

    class Meta:
        db_table='result'
        app_label = u'risk'
        verbose_name_plural = u'实时风控结果'

class TradeManage(models.Manager):
    def get_query_set(self):
        return super(type(self),self).get_query_set().exclude(userid = 10094).exclude(userid = 2002)


class TradeRecord(models.Model):
    CARD_TYPE_CHOICES = (
        (1,'借记卡'),
        (2,'信用卡'),
        (3,'准贷记卡'),
        (4,'储值卡'),
    )

    id = models.AutoField(primary_key=True)
    busicd = models.CharField(u'交易类型',max_length=6,default='',choices=BUSICD_CHOICES)
    userid = models.IntegerField(u'用户ID')
    terminalid = models.CharField(u'设备ID',max_length=20, default='')
    psamid = models.CharField(u'PSAMid',max_length=20, default='')
    appid = models.CharField(u'appid客户端（激活）编号',max_length=40,default='')
    udid = models.CharField(u'手机udid号',max_length=20, default='')
    txamt = models.IntegerField(u'交易金额',default=0)
    txcurrcd = models.CharField(u'交易币种',max_length=3)
    sysdtm = models.DateTimeField(u'交易时间（交易系统）')
    syssn = models.CharField(u'交易流水号',max_length=14)
    txdtm = models.DateTimeField(u'登陆时间（客户系统）')
    txzone = models.CharField(u'交易时区',max_length=3)
    debitacntname = models.CharField(u'借记卡姓名',max_length=64, blank=True, null=True)
    debitacntbank = models.CharField(u'借记卡开户行',max_length=64, blank=True, null=True)
    debitacntcd = models.CharField(u'借记卡卡号',max_length=19)
    creditacntcd = models.CharField(u'信用卡卡号',max_length=19)
    longitude = models.FloatField(u'经度')
    latitude = models.FloatField(u'纬度')
    authid = models.CharField(u'授权号',max_length=6)
    respcd = models.CharField(u'交易系统返回码',max_length=4)
    cardcd = models.CharField(u'交易卡号',max_length=19)
    cardtp = models.IntegerField(u'交易卡类型',choices=CARD_TYPE_CHOICES)
    riskret = models.CharField(u'风控返回码',max_length=6, default='000000')

    objects = TradeManage()

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

   
    def trans_date(self):
        return self.sysdtm
   
    trans_date.short_description='交易时间（交易系统）'
    trans_date.admin_order_field='sysdtm'
    
    def display_txamt(self):
        return float(self.txamt)/100
    display_txamt.short_description='交易金额'
    display_txamt.admin_order_field='txamt'

    def display_riskret(self):
        return display_base(self.riskret)
    display_riskret.short_description='风控返回码'
    display_riskret.admin_order_field='riskret'

    def display_respcd(self):
        try:
            record = RiskCode.objects.get(code=self.respcd)
            return record.name
        except:
            return self.respcd

    display_respcd.short_description='交易系统返回码'
    display_respcd.admin_order_field='respcd'
    
    class Meta:
        db_table='traderecord'
        app_label = u'risk'
        verbose_name_plural = u'商户交易纪录'

class LoginRecord(models.Model):
    lid = models.AutoField(primary_key=True)
    userid = models.IntegerField('用户编号')
    terminalid = models.CharField('终端编号',max_length=20)
    psamid = models.CharField('PSAM编号',max_length=12)
    appid = models.CharField('客户端编号',max_length=40)
    udid = models.CharField('手机UDID号',max_length=20)
    longitude = models.FloatField(u'经度')
    latitude = models.FloatField(u'纬度')
    respcd = models.CharField(u'交易系统返回码',max_length=4)
    txdtm = models.DateTimeField(u'登录时间（客户系统）',blank=True)
    txzone = models.CharField(u'交易时区',max_length=5)
    sysdtm = models.DateTimeField(u'交易时间（交易系统）')
    riskret = models.CharField(u'风控返回码',max_length=6)
    
    #import pdb
    #pdb.set_trace()
    def trans_sysdate(self):
        return self.sysdtm
    trans_sysdate.short_description='交易时间（交易系统）'
    trans_sysdate.admin_order_field='sysdtm'
    
    def display_riskret(self):
        return display_base(self.riskret)
    display_riskret.short_description='风控返回码'
    display_riskret.admin_order_field='riskret'

    def display_respcd(self):
        return display_base(self.respcd)
    display_respcd.short_description='交易系统返回码'
    display_respcd.admin_order_field='respcd'
    
    class Meta:
        db_table='loginrecord'
        app_label = u'risk'
        verbose_name_plural = u'商户登录纪录'

class UserParam(models.Model):
    id = models.AutoField(primary_key = True)
    userid = models.IntegerField('用户名') 
    type = models.SmallIntegerField(u'用户类型')
    city = models.CharField(u'所在城市',blank=True, max_length=20)
    latitude = models.FloatField(u'纬度',blank=True)
    longitude = models.FloatField(u'经度',blank=True)
    dayamount = models.IntegerField(u'日限额',default=-1)
    weekamount = models.IntegerField(u'周限额',default=-1)
    monthamount = models.IntegerField(u'月限额',default=-1)
    daycount=models.IntegerField(u'日限次')
    weekcount=models.IntegerField(u'周限次',blank=True)
    monthcount = models.IntegerField(u'月限次')
    dayauth = models.IntegerField(u'日授权次数')
    weekauth = models.IntegerField(u'周授权次数')
    monthauth = models.IntegerField(u'月授权次数')
    daycreditcount = models.IntegerField(u'信用卡日交易限次数')
    weekcreditcount = models.IntegerField(u'信用卡周交易限次数')
    monthcreditcount = models.IntegerField(u'信用卡月交易限次数')
    daycreditamount = models.IntegerField(u'信用卡日收款限额',default=-1)
    weekcreditamount = models.IntegerField(u'信用卡周收款限额',default=-1)
    monthcreditamount = models.IntegerField(u'信用卡月收款限额',default=-1)
    daydebitrate = models.FloatField(u'日借记卡金额比例')
    weekdebitrate = models.FloatField(u'周借记卡金额比例')
    monthdebitrate = models.FloatField(u'月借记卡金额比例')
    daycreditrate = models.FloatField(u'日信用卡金额比例')
    weekcreditrate = models.FloatField(u'周信用卡金额比例')
    monthcreditrate = models.FloatField(u'月信用卡金额比例')
    loginpwderr = models.IntegerField(u'登录密码错误次数')
    adminpwderr = models.IntegerField(u'管理密码错误次数')
    smalltranserr = models.IntegerField(u'多次小金额错误次数')
    allowedamount = models.IntegerField(u'单笔交易限额',default=-1)
    
    def display_allowedamount(self):
        return float(self.allowedamount)/100

    display_allowedamount.short_description='单笔交易限额'
    display_allowedamount.admin_order_field='allowedamount'
    class Meta:
        db_table = 'userparam'
        app_label = u'risk'
        verbose_name_plural = u'商户风控参数'

class UserDay(models.Model):
    nid = models.AutoField(primary_key=True)
    userid = models.IntegerField(u'商户ID')
    tradecyc = models.CharField(u'交易周期',max_length=8)
    tradecount = models.CharField(u'交易总次数',max_length=11)
    tradeamount = models.CharField(u'交易总金额',max_length=11)
    debitcount = models.CharField(u'借记卡总次数',max_length=11)
    debitamount = models.CharField(u'借记卡总金额',max_length=11)
    creditcardcount = models.CharField(u'信用卡总次数',max_length=11)
    creditcardamount = models.CharField(u'信用卡总金额',max_length=11)
    intcount = models.CharField(u'整数交易次数',max_length=11)
    intamount = models.CharField(u'整数交易金额',max_length=11)
    workdatecount = models.CharField(u'工作日总次数',max_length=11)
    workdateamount = models.CharField(u'工作日总金额',max_length=11)
    nodtaacount = models.CharField(u'非工作日总次数',max_length=11)
    nodataamount = models.CharField(u'非工作日总金额',max_length=11)
    worktimecount = models.CharField(u'工作时间段总次数',max_length=11)
    worktimeamount = models.CharField(u'工作时间段总金额',max_length=11)
    notimecount = models.CharField(u'非工作时间段总次数',max_length=11)
    notimeamount = models.CharField(u'非工作时间段总金额',max_length=11)
    areacount = models.CharField(u'区域内笔数',max_length=11)
    areaamount = models.CharField(u'区域内金额',max_length=11)
    noareacount = models.CharField(u'非区域内笔数',max_length=11)
    noareaamount = models.CharField(u'非区域内金额',max_length=11)
    balancequerycount = models.CharField(u'余额查询笔数',max_length=11)
    passerrcount = models.CharField(u'交易密码错误次数',max_length=11)
    balancelackcount = models.CharField(u'余额不足笔数',max_length=11)
    authcount = models.CharField(u'授权笔数',max_length=11)
    allowedcount = models.CharField(u'单笔超额笔数',max_length=11)
    dividecount = models.CharField(u'分单笔数',max_length=64)
    loginpwderr = models.CharField(u'登录密码错误次数',max_length=64)
    tradeexceedcount=models.CharField(u'日金额超限笔数',max_length=64)
    tradeexceedamocount=models.CharField(u'日超限笔数',max_length=64)
    creditexceedcount=models.CharField(u'日信用卡金额超限笔数',max_length=64)
    creditexceedamocount =models.CharField(u'日信用卡超限笔数',max_length=64)
    creditescalehigh =models.CharField(u'日信用卡比率超限笔数',max_length=64)
    createtime = models.DateTimeField(u'创建时间')
    createadminnid = models.IntegerField(u'创建账号')
    lastmodifytime = models.DateTimeField(u'最后修改时间')
    lastmodifyadminnid = models.IntegerField(u'最后修改账号')
    deltag = models.IntegerField(u'删除标记')

    def display_debitamount(self):
        return float(self.debitamount)/100
    display_debitamount.short_description='借记卡总金额'
    display_debitamount.admin_order_field='debitamount'

    def display_tradeamount(self):
        return float(self.tradeamount)/100
    display_tradeamount.short_description='交易总金额'
    display_tradeamount.admin_order_field='tradeamount'

    def display_creditcardamount(self):
        return float(self.creditcardamount)/100
    display_creditcardamount.short_description='信用卡总金额'
    display_creditcardamount.admin_order_field='creditcardamount'

    def display_intamount(self):
        return float(self.intamount)/100
    display_intamount.short_description='整数交易金额'
    display_intamount.admin_order_field='intamount'

    def display_worktimeamount(self):
        return float(self.worktimeamount)/100

    def display_notimeamount(self):
        return float(self.notimeamount)/100
    display_notimeamount.short_description='非工作时间段总金额'
    display_notimeamount.admin_order_field='notimeamount'

    def display_noareaamount(self):
        return float(self.noareaamount)/100
    display_noareaamount.short_description='非区域内金额'
    display_noareaamount.admin_order_field='noareaamount'

    class Meta:
        db_table = 'userday_20120319'
        app_label = u'risk'
        verbose_name_plural = u'商户风控日报表'

class CoreLevel(models.Model):
    '''
    商户等级表
    '''
    level = models.IntegerField(u'等级',primary_key=True)
    
    dayamount = models.BigIntegerField(u'日收款金额',default=0)
    weekamount = models.BigIntegerField(u'周收款金额',default=0)
    monthamount = models.BigIntegerField(u'月收款金额',default=0)
    
    daycount = models.IntegerField(u'日收款次数',default=0)
    weekcount = models.IntegerField(u'周收款次数',default=0)
    monthcount = models.IntegerField(u'月收款次数',default=0)
    
    dayauthcount = models.IntegerField(u'日授权次数',default=0)
    weekauthcount = models.IntegerField(u'周授权次数',default=0)
    monthauthcount = models.IntegerField(u'月授权次数',default=0)
    
    daycreditamount = models.BigIntegerField(u'信用卡日交易金额',default=0)
    weekcreditamount = models.BigIntegerField(u'信用卡周交易金额',default=0)
    monthcreditamount = models.BigIntegerField(u'信用卡月交易金额',default=0)
    
    daycreditcount = models.IntegerField(u'信用卡日交易次数',default=0)
    weekcreditcount = models.IntegerField(u'信用卡周交易次数',default=0)
    monthcreditcount = models.IntegerField(u'信用卡月交易次数',default=0)
    
    daycreditrate = models.IntegerField(u'信用卡日交易比例',default=0)
    weekcreditrate = models.IntegerField(u'信用卡周交易比例',default=0)
    monthcreditrate = models.IntegerField(u'信用卡月交易比例',default=0)
    
    daycardamount = models.BigIntegerField(u'单一卡日交易金额',default=0)
    weekcardamount = models.BigIntegerField(u'单一卡周交易金额',default=0)
    monthcardamount = models.BigIntegerField(u'单一卡月交易金额',default=0)
    
    daycardcount = models.IntegerField(u'单一卡日交易次数',default=0)
    weekcardcount = models.IntegerField(u'单一卡周交易次数',default=0)
    monthcardcount = models.IntegerField(u'单一卡月交易次数',default=0)
    
    validdate = models.IntegerField(u'有效营业日期',default=0)
    validtime = models.IntegerField(u'有效营业时间',default=0)
    validarea = models.IntegerField(u'有效营业地区',default=0)
    
    last_modify = models.DateTimeField(u'最后修改时间',auto_now=True)
    last_admin = models.IntegerField(u'最后修改人UID',default=0)
    is_delete = models.SmallIntegerField(u'是否删除',default=0)

    maxamount = models.IntegerField(u'借记卡单笔最大交易金额',default = 500000)
    creditmaxamount = models.IntegerField(u'信用卡单笔最大交易金额',default = 500000)
    daybebitcount = models.IntegerField(u'单一卡日交易笔数（借记卡）',default = 5)
    weekbebitcount = models.IntegerField(u'单一卡周交易笔数（借记卡）',default = 20)
    monthbebitcount = models.IntegerField(u'单一卡月交易笔数（借记卡）',default = 60)
    daybebitamount = models.IntegerField(u'单一卡日交易金额（借记卡）',default = 500000)
    weekbebitamount = models.IntegerField(u'单一卡周交易金额（借记卡）',default = 1000000)
    monthbebitamount = models.IntegerField(u'单一卡月交易金额（借记卡）',default = 15000000)


    def display_dayamount(self):
        return float(self.dayamount)/100
    display_dayamount.short_description='日收款金额'
    display_dayamount.admin_order_field='dayamount'

    def display_weekamount(self):
        return float(self.weekamount)/100
    display_weekamount.short_description='周收款金额'
    display_weekamount.admin_order_field='weekamount'

    def display_monthamount(self):
        return float(self.monthamount)/100
    display_monthamount.short_description='月收款金额'
    display_monthamount.admin_order_field='monthamount'

    def display_daycardamount(self):
        return float(self.daycardamount)/100
    display_daycardamount.short_description='单一卡日交易金额'
    display_daycardamount.admin_order_field='daycardamount'

    def display_weekcardamount(self):
        return float(self.weekcardamount)/100
    display_weekcardamount.short_description='单一卡周交易金额'
    display_weekcardamount.admin_order_field='weekcardamount'

    def display_monthcardamount(self):
        return float(self.monthcardamount)/100
    display_monthcardamount.short_description='单一卡月交易金额'
    display_monthcardamount.admin_order_field='monthcardamount'

    class Meta:
        db_table = 'level'
        verbose_name = u'商户等级表'
        verbose_name_plural = u'商户等级'

class Risk(models.Model):
    id = models.IntegerField(primary_key = True)
    tradetype = models.IntegerField(u'允许交易类型',default=1)
    cardtype = models.IntegerField(u'允许交易卡类型',default=1)
    currency = models.IntegerField(u'允许交易货种',default=1)
    validdate = models.IntegerField(u'有效营业日期',default=1)
    validtime = models.IntegerField(u'有效营业时间',default=1)
    validarea = models.IntegerField(u'有效营业地区',default=1)
    maxamount = models.IntegerField(u'单笔最大交易金额',default=500000)
    creditmaxamount = models.IntegerField(u'信用卡单笔最大交易金额',default=500000)
    maxpassworderr = models.IntegerField(u'登录密码错误次数',default=3)
    smallamount = models.IntegerField(u'X:小额交易定义：小于X',default=100)
    alarmcreditrate = models.IntegerField(u'信用卡交易预警金额比率%例：50即50%',default=50)
    alarmintrate = models.IntegerField(u'整数交易预警金额比例%',default=50)
    dividecount = models.IntegerField(u'超限后允许交易次数（分单）',default=1)
    paymentdaycount = models.IntegerField(u'持卡人日付款限次',default=30)
    def display_maxamount(self):
        return float(self.maxamount)/100

    def display_creditmaxamount(self):
        return float(self.creditmaxamount)/100
    display_maxamount.short_description='单笔最大交易金额'
    display_maxamount.admin_order_field='maxamount'
    
    display_creditmaxamount.short_description='信用卡单笔最大交易金额'
    display_creditmaxamount.admin_order_field='creditmaxamount'
    class Meta:
        db_table = 'risk'
        verbose_name = u'风控设置'
        verbose_name_plural = u'风控设置'

class RiskCode(models.Model):
    IS_DELETE_CHOICES = (
        (0,u'正常'),
        (1,u'删除'),
    )
    nid = models.IntegerField(u'代码ID',primary_key = True)
    code = models.CharField(u'代码',max_length = 40)
    name = models.CharField(u'代码名称',max_length = 500)
    parentnid = models.IntegerField(u'父ID',blank=True,null=True)
    desc = models.CharField(u'代码说明',max_length = 500)
    remark1 = models.CharField(u'备注1',max_length = 500)
    remark2 = models.CharField(u'备注2',max_length = 500)
    remark3 = models.CharField(u'备注3',max_length = 500)
    last_modify = models.DateTimeField(u'最后变更时间',auto_now = True)
    last_admin = models.IntegerField(u'最后变更人ID',default = 0)
    is_delete = models.SmallIntegerField(u'是否删除',choices = IS_DELETE_CHOICES)
    class Meta:
        db_table = 'riskcode'
        verbose_name_plural = u'风控编码'

#coding=utf-8
from django.contrib.auth.models import User

from util import fields

from django.db import models

class Appinfo(models.Model):
    APPINFO_UPDATE_TYPE_CHOICES=(
        (0,u'强制'),
        (1,u'自动'),
        (2,u'自选'),
    )
    app_name = models.CharField(u'软件名称',max_length=40)
    app_ver = models.CharField(u'软件版本',max_length=40)
    app_minver = models.CharField(u'软件版本',max_length=40)
    os = models.CharField(u'操作系统类型',max_length=12)
    os_ver = models.CharField(u'版本',max_length=32)
    update_type = models.SmallIntegerField(u'强制更新',choices=APPINFO_UPDATE_TYPE_CHOICES)
    domain = models.CharField(u'API地址',max_length=128)
    url = models.CharField(u'程序下载路径URL',max_length=1024)
    description = models.CharField(u'描述',max_length=1024)
    upload_retries = models.IntegerField(u'上传重试次数',default=10)
    reversal_retries = models.IntegerField(u'重试重试次数',default=10)
    online_timeout = models.IntegerField(u'联机超时',default=50)
    offline_timeout = models.IntegerField(u'非联机超时',default=20)
    create_time = models.DateTimeField(u'创建时间',auto_now=True)
    create_admin = models.IntegerField(u'创建人ID',default=10000)
    class Meta:
        db_table = 'appinfo'
        verbose_name_plural = u'客户端版本管理'

class Stat(models.Model):
    busicd = models.CharField(u'交易类型',max_length=6)
    userid = models.IntegerField(u'用户ID')
    terminalid = models.CharField(u'终端编号',max_length=20)
    udid = models.CharField(u'手机UDID号',max_length=40)
    appver = models.CharField(u'客户端版本',max_length=32)
    phonemodel = models.CharField(u'手机模式',max_length=64)
    networkmodel = models.CharField(u'网络模式',max_length=16)
    os = models.CharField(u'操作系统',max_length=16)
    osver = models.CharField(u'操作系统版本',max_length=16)
    errorcd = models.CharField(u'错误码',max_length=2)
    errormsg = models.CharField(u'错误信息',max_length=1024)
    class Meta:
        db_table = 'stat'
        verbose_name_plural = u'客户端日志'

class FeedBack(models.Model):
    nid = models.AutoField(primary_key=True)
    busicd = models.CharField(u'交易类型',max_length=6)
    userid = models.IntegerField(u'用户编号')
    terminalid = models.CharField(u'终端编号',max_length=20, blank=True)
    appid = models.CharField(u'客户端编号',max_length=40)
    udid = models.CharField(u'手机UDID',max_length=40)
    appver = models.CharField(u'客户端版本',max_length=16)
    phonemodel = models.CharField(u'手机模式',max_length=64, blank=True)
    networkmode = models.CharField(u'网络模式',max_length=16, blank=True)
    os = models.CharField(u'操作系统',max_length=16)
    osver = models.CharField(u'操作系统版本',max_length=16,blank=True)
    feedbackcd = models.CharField(u'反馈码',max_length=2)
    feedbackmsg = models.CharField(u'反馈信息',max_length=1024)
    class Meta:
        db_table = 'feedback'
        verbose_name_plural = u'用户反馈'
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


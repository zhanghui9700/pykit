#coding=utf-8

import random, datetime,pdb,logging,json

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User

from util import fields
from util.define import NextLevelAfterBasicLevel,UserType,UPGRADE_IMAGE,UPGRADE_STATE,UserState,LICENSE_TYPE,ApplyState,GROUP_ID,TerminalUsedState,TerminalState,BuyType,GROUP_CHOICES
from util.imgstore import save_image
from core.models import UserProxy,Recharge,TerminalBind

_logerror = logging.getLogger('my_error')

UTYPE_CHOICES=(
    (1,u'个人'),
    (2,u'个体户'),
    (3,u'公司')
)
SRC_CHOICES=(
    ('10001',u'钱方直营'),
    ('10002',u'山东渠道'),
    ('10003',u'神码渠道'),
    ('10004',u'北京电信'),
    ('10005',u'天顺名扬'),
    ('10006',u'脉动无限'),
    ('10007',u'梦翔明日'),
    ('10008',u'钱方测试'),
    ('10009',u'北京京拍档'),
    ('10010',u'沈阳新华银'),
    ('10011',u'北京致远鸿图'),
    ('10012',u'福州福铁'),
    ('10013',u'南通杰盛'),
)

def save_multi_db(model_class):
    def save_wrapper(save_func):
        def new_save(self, *args, **kwargs):
            super(model_class,self).save(using = 'mis')
        return new_save
    func = getattr(model_class, 'save')
    setattr(model_class, 'save', save_wrapper(func))
    return save_wrapper

# Create your models here.
class CodeManager(models.Manager):
    def generate_code(self, mobile, email=''):
        now = datetime.datetime.now()
        code = random.randint(0, 1000000)
        code = '%06d' % code
        vc = self.model(code=code, email=email, mobile=mobile,
            flag=0, created=now)
        vc.save(using=self._db)
        return code

class ApplyManager(models.Manager):
    def get_query_set(self):
        return super(type(self),self).get_query_set()
        
class Apply(models.Model):
    STATE_CHOICES=(
        (0,u'已注册'),
        (1,u'已填写信息'),
        (4,u'等待审核'),
        (5,u'审核通过'),
        (6,u'自动审核失败，待人工审核'),
        (7,u'审核失败（人工）'),
        (8,u'等待复审'),
    )

    AUTH_CHOICE = (
    (1, u'授权'),
    (2, u'无授权'),
    )
    CHECK_CHOICE = (
    (1, u'通过年检'),
    (2, u'未通过年检'),
    )

    BANKTYPE_CHOICES=(
        (1,u'对私'),
        (2,u'对公'),
    ) 
    
    ALLOW_AREA_CHOICE = (
        ('0', u'本市'),
        ('1', u'全国'),
    )

    usertype = models.SmallIntegerField(u"用户类型",default=1,choices=UTYPE_CHOICES)
    user = fields.ForeignKeyAcrossDB(User, primary_key=True)
    mobile = models.CharField(u'手机号(*)',max_length=11, null=True, blank=True)
    name = models.CharField(u"用户名(*)",max_length=32, null=True, blank=True,help_text=u'个人用户名/字号/公司名称')
    nickname = models.CharField(u'收据显示名称',max_length=64,blank=True,null=True)
    
    address = models.CharField(u'经营地址(*)',max_length=256, null=True, blank=True,help_text=u'',default=' ')
    contact = models.CharField(u'联系人（可附身份证号*）',max_length=32, null=True, blank=True,default=' ')
    post = models.CharField(u'邮政编码(*)',max_length=10, null=True, blank=True,default='100001')
    edu = models.SmallIntegerField(u'教育背景',null=True, blank=True,default=1)
    monthincome = models.SmallIntegerField(u'月收入',default=0, null=True, blank=True)
    monthexpense = models.SmallIntegerField(u'月消费',default=0, null=True, blank=True)
    
    province = models.CharField(u'注册省份', max_length=10, blank=True)
    city = models.CharField(u'注册城市',max_length=32, null=True, blank=True)
    businessaddr = models.CharField(u'*注册地址',max_length=256, null=True, blank=True)
    telephone = models.CharField(u'联系人电话',max_length=32, null=True, blank=True )  
    legalperson = models.CharField(u"法人姓名(*)",max_length=32, null=True, blank=True,help_text=u'个人用户填写用户姓名',default=' ') 
    idnumber = models.CharField(u'法人身份证(*)',max_length=20, null=True, blank=True)
    idstatdate = models.DateField(u'法人身份证有效期开始',null=True, blank=True,default=datetime.datetime.now())
    idenddate = models.DateField(u'法人身份证有效期结束',null=True, blank=True,default=datetime.datetime.now())
    idphoto1 = models.ImageField(u"法人身份证正面",max_length=50,upload_to="img/", blank=True, null=True)
    idphoto2 = models.ImageField(u"法人身份证反面",max_length=50,upload_to="img/", blank=True, null=True)
    
    licensenumber = models.CharField(u'营业执照号',max_length=20, null=True, blank=True)
    licenseend_date = models.DateField(u'营业执照有效期',blank=True, null=True,default=datetime.datetime.now())
    licensephoto = models.ImageField(u'营业执照有效件',max_length=50,upload_to="userinfo/", blank=True, null=True)
    
    taxnumber = models.CharField(u'税务登记证编号',max_length=40, null=True, blank=True)
    taxenddate = models.DateField(u'税务登记证有效期',blank=True, null=True,default=datetime.datetime.now())
    taxphoto = models.ImageField(u'税务登记证扫描件',max_length=50,upload_to="userinfo/", blank=True, null=True)
     
    orgcode = models.CharField(u'组织机构号',max_length=20, null=True, blank=True)
    mcc = models.CharField(u'出售的商品或服务mcc',max_length=32, null=True,blank=True)
    
    banktype = models.SmallIntegerField(u'清算银行类型',default=1, choices=BANKTYPE_CHOICES)
    bankname = models.CharField(u'开户银行(*)',max_length=256, null=True, blank=True)
    bankuser = models.CharField(u'开户人姓名或公司(*)',max_length=32,null=True,blank=True)
    bankaccount = models.CharField(u'开户银行卡号(*)',max_length=32, null=True, blank=True)
    
    state = models.SmallIntegerField(u'状态',default=0, choices=STATE_CHOICES)
    src = models.CharField(u'推荐来源',default='10001',max_length=15,choices=SRC_CHOICES)
    groupid = models.IntegerField(u'渠道',default='10001',choices=GROUP_CHOICES)
    terminalcount = models.IntegerField(u'读卡器数量',default=1)
    logisticaddr = models.CharField(u'配送地址',max_length=256,null=True,blank=True)
    creditbank = models.CharField(u'信用卡开户行',help_text=u'个人信用资质证明，非必填',max_length=64,blank=True)
    creditcard = models.CharField(u'信用卡号',max_length=20, null=True, blank=True)
    email = models.EmailField(u'电子邮箱',max_length=75, null=True, blank=True)
    latitude = models.FloatField(u'纬度',null=True, blank=True)
    longitude = models.FloatField(u'经度',null=True, blank=True)
    provision = models.CharField(u'经营范围', max_length=256,default=' ') 
    allowarea = models.CharField(u'开通区域',max_length=20,default='0',blank=True,help_text=u'0本市1全国',choices=ALLOW_AREA_CHOICE)
    debitfee = models.FloatField(u'借记卡手续费',default=0.01)
    creditfee = models.FloatField(u'信用卡手续费', default=0.01)
    debitlimit= models.FloatField(u'借记卡封顶', default=25.0)
    creditlimit = models.FloatField(u'信用卡封顶', default=25.0)
    tid = models.CharField(u'终端编号', max_length=256,blank=True)
    needauth = models.SmallIntegerField(u'是否需要授权',blank=True,default=2,choices=AUTH_CHOICE)
    passcheck = models.SmallIntegerField(u'是否通过年检',blank=True,default=2, choices=CHECK_CHOICE)
    founddate = models.DateField(u'公司成立日期',blank=True,null=True,default=datetime.datetime.now())
    area = models.FloatField(u'店面面积',default=100.0) 
    
    last_admin = models.IntegerField(u'最后修改人',null=False,blank=True,default=0)
    last_modify = models.DateTimeField(u'最后变更日期',auto_now=True)
    ext = models.TextField(u'扩展字段',null=True,blank=True)

    monthtradeamount = models.IntegerField(u'月交易金额',null=True,blank=True)
    uploadtime = models.DateTimeField(u'上传时间',null=True,blank=True)
    firstaudittime = models.DateTimeField(u'初次审核时间',null=True,blank=True)
    lastaudittime = models.DateTimeField(u'最后一次审核时间',null=True,blank=True)
    
    objects = ApplyManager()

    def audit_passed(self,admin_id):
        u = UserProxy.objects.get(pk=self.user)
        pk = u.create_profile(self,admin_id)
        user = User.objects.filter(pk=self.user)
        if user[0].user_type == 1:
            user.update(user_level = 2)
        elif user[0].user_type == 2 or user[0].user_type ==3:
            user.update(user_level = 4)
        else:
            pass

        if pk > 0:
            try:
                sa=AuditLog(user_id = self.user,
                            ext_key = self.user,
                            type = 1,
                            result=1,
                            memo=u'审核成功',
                            create_user=admin_id,
                            groupid = self.groupid,
                            create_date=datetime.datetime.now())        
                sa.save()
            except:
                pass

            if not self.firstaudittime:
                self.firstaudittime = datetime.datetime.now()
            self.lastaudittime = datetime.datetime.now()
            self.save()

            #神码渠道专用
            if self.src == str(GROUP_ID.Shenma):
                if not self.audit_shenma():
                     _logerror.error(u'神码用户绑定读卡器出错,UID:%s,TID:%s'%(self.user,self.tid))

        return pk
    
    def audit_shenma(self):
        '''TODO 1.插入读卡器购买记录。2.绑定读卡器。'''
        #读卡器绑定
        result = True
        try:
            self.terminalbind()
            self.create_charge()
        except Exception,ex:
            result = False
            _logerror.exception(ex)
        
        return result
        
    def create_charge(self):
        ch = Recharge.objects.filter(userid = self.user)
        if ch.count() > 0:
            ch[0].update(type=BuyType.SHENMA,fee=0,desc=u"神码渠道用户不需要购买读卡器",status=1)
        else:
            charge = Recharge(userid = self.user,
                                type=BuyType.SHENMA,
                                fee=0,
                                desc=u"神码渠道用户不需要购买读卡器",
                                status=1)
            charge.save()

    #读卡器绑定
    def terminalbind(self):
        try:user = User.objects.get(id=self.user)
        except:raise Exception(u'不存在ID为%s的用户' % self.user)
        from mis.models import Terminal,Psam
        
        try: t = Terminal.objects.get(terminalid=self.tid)
        except:raise Exception(u'shenma terminalbindnot exists terminal:%s' % self.tid)
        
        if t.used == TerminalUsedState.AssignedPasm \
            and t.state == TerminalState.Normal:
            psam = Psam.objects.get(psamid=t.psamid)
            tb = TerminalBind.objects.create(user = user,
                                             udid = user.username,
                                             terminalid = t.terminalid,
                                             psamid=psam.psamid,
                                             psamtp = psam.psamtp,
                                             tckkey = t.tck,
                                             pinkey1 = psam.pinkey1,
                                             pinkey2 = psam.pinkey2,
                                             mackey = psam.mackey,
                                             diskey = psam.diskey,
                                             fackey = u'%s%s' % (psam.producer,psam.model),
                                             ) 
            if tb.pk > 0:
                t.user = user.id
                t.used = TerminalUsedState.AssignedUser
                t.save()
            else:
                raise Exception(u'shenma save teminalbind error!')
        return tb.pk

    def audit_failed(self,admin_id,failedmsg):
        try:
            sa=AuditLog(user_id= self.user,
                        ext_key = self.user,
                        type = 1,
                        result=0,
                        memo=failedmsg,
                        groupid = self.groupid,
                        create_user=admin_id,
                        create_date=datetime.datetime.now())        
            sa.save()
            self.state = ApplyState.AUDIT_FAILURE

            if not self.firstaudittime:
                self.firstaudittime = datetime.datetime.now()
            self.lastaudittime = datetime.datetime.now()

            self.save()

            return True
        except:
            return False

    def display_auditinfo(self):
        log = AuditLog.objects.filter(user_id=self.user).order_by("-id")
        if log:
            return log[0].memo
        else:
            return ''
    display_auditinfo.short_description = u'审核信息'

    def display_user_name(self):
        try:
            u = User.objects.get(pk=self.user)
            return u.username
        except:
            return '-----'
    display_user_name.short_description = u'登录名'

    class Meta:
        db_table = 'apply'
        verbose_name = u'商户申请表'
        verbose_name_plural = u'商户申请审核'
           
class ApplyCode(models.Model):
    code = models.CharField(u'邀请码',max_length=32,help_text=u'不输入系统自动生成邀请码')
    city = models.CharField(u'城市',max_length=32,default='010')
    src = models.CharField(u'推广渠道',max_length=16,default='10001',choices=SRC_CHOICES)
    usertype = models.SmallIntegerField(u'用户类型',choices=UTYPE_CHOICES)
    mcc = models.CharField(u'mcc',max_length=32,default='9999')
    used = models.SmallIntegerField(u'可使用次数',default=1)

    terminalid = models.CharField(u'终端编号',max_length=32,default='',help_text=u'此邀请码对应的读卡器ID，可为空，针对类似神码渠道用户',blank=True)
    
    class Meta:
        db_table = 'audit_applycode'
        db_tablespace = u'mis'
        verbose_name_plural = u'商户邀请码'


class VerifyCode(models.Model):
    mobile = models.CharField(u'手机号',max_length=32, blank=True)
    email = models.EmailField(u'电子邮箱地址',max_length=75, blank=True)
    code = models.CharField(u'验证码',max_length=16)
    flag = models.SmallIntegerField(u'状态',default=0) #0 init 1 used
    created = models.DateTimeField(u'创建时间',auto_now_add=True)
    objects = CodeManager()

    class Meta:
        db_table = 'veriycode'
        #app_label= u'useraudit'
        db_tablespace=u'mis'
        verbose_name_plural = u'短信验证码'

class Upgrade(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = fields.ForeignKeyAcrossDB(User)
    up_source = models.SmallIntegerField(u'申请方式',default=0)      #申请方式0网络申请
    original_level = models.SmallIntegerField(u'升级时等级',default=0) #升级时的等级
    apply_level = models.SmallIntegerField(u'要升级到的等级',default=0)    #要升级到的等级
    state = models.SmallIntegerField(u'状态',default=0)          #0待审,1通过,2自动审核失败3人工拒绝 
    auditor = models.IntegerField(u'审核人ID',default=0)             #审核人ID，默认0(0为自动审核)
    audittime = models.DateTimeField(u'审核时间',auto_now=True)  #审核时间now
    submit_time = models.DateTimeField(u'提交时间',auto_now_add=True)#提交时间
    need_typist = models.SmallIntegerField(u'是否需要录入凭证',default=0)    #是否需要录入凭证 0不需要 1需要
    input_state = models.SmallIntegerField(u'凭证录入状态',default=0)    #凭证录入状态0待录入1完毕
    memo = models.CharField(u'备注',max_length=256)              #备注，审核结果
    
    def approved(self,user):
        self.state = UPGRADE_STATE.PASSED
        self.auditor = user.id
        self.memo = u'升级审批-人工-审批通过'
        #print self.memo
        self.save()
        return True

    def refused(self,user):
        self.state = UPGRADE_STATE.REFUSED
        self.memo = u'升级审批-人工-拒绝审批'
        self.auditor = user.id
        self.memo
        self.save()

        #print self.memo
        return True

    def blacklist(self,user):
        self.state = UPGRADE_STATE.REFUSED
        self.memo = u'升级审批-人工-加入黑名单'
        self.auditor = user.id
        self.memo
        self.save()
        User.objects.get(pk=user_id).update(state=UserState.BLACKLIST)
        #print self.memo
        return True

    class Meta:
        db_table = 'mis_upgrade'
        #app_label= u'useraudit'
        verbose_name_plural = u'商户升级审核'

class UpgradeProxy(Upgrade):
    def get_auto_audit_up(self):
        '''
        获取自动审批的升级列表
        '''
        return Upgrade.objects.filter(state=UPGRADE_STATE.WAIT_AUDIT,input_state = 1)[0:10]
    def get_up_voucher(self):
        '''
        获取一个升级关联的凭证信息
        '''
        return UpgradeVoucher.objects.filter(upgrade_id=self)

    def get_next_level(self,user):
        '''
        根据用户当前等级获取升级的对应等级
        '''
        if user.user_level == 1:
            return NextLevelAfterBasicLevel 
        else:
            return user.user_level + 1

    def can_upgrade(self,user):
        '''
        用户是否能够发起升级请求，没有等待审核状态的升级就可以
        '''
        upQS = Upgrade.objects.filter(user_id = user.id).exclude(state = 1)
        return len(upQS) == 0 

    def is_valid(self,user,upgrade):
        '''
        是否可以升级，包括凭证检查和是否重复申请
        '''
        if not self.can_upgrade(user):
            raise Exception(u'您的升级请求正在审核中，请耐心等待！')
            
        voucherQS = UpgradeVoucher.objects.filter(user_id=upgrade.user_id,apply_level=upgrade.apply_level)
        if len(voucherQS) != UPGRADE_IMAGE.UPGRADE_COUNT_FOR_UPGRADE.get('USER_TYPE_'+str(user.user_type),0):
            raise Exception(u'上传凭证不完整，请续传凭证后继续升级！')
        
        return True;

    def create_up(self,upgrade=None):
        '''
        保存一个升级请求，并更新升级关联的凭证外键关系
        '''
        result = False
        try: 
            up = upgrade;
            try:
                up.save()
            except Exception,e:
                _logeroor.exception(e)
            if up.id > 0 :
                UpgradeVoucher.objects.filter(user_id=up.user_id,apply_level=up.apply_level).update(upgrade_id=up.id)
                result = True
        except Exception,e:
            _logerror.exception(e)

        return result
    class Meta:
        proxy = True

class UpgradeVoucher(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = fields.ForeignKeyAcrossDB(User)
    upgrade_id = models.ForeignKey(Upgrade,db_column='upgrade_id',default=0)
    apply_level = models.SmallIntegerField(u'要升级到的等级',default=0)
    cert_type = models.SmallIntegerField(u'证件类别',default=0)
    name = models.CharField(u'凭证图片',max_length=30, blank=True)#图片文件名
    submit_time = models.DateTimeField(u'提交时间',auto_now_add = True)
    state = models.SmallIntegerField(u'状态',default=0) #0待审1通过2不清晰3不合格
    input_state = models.IntegerField(u'凭证录入状态',default=0) #凭证录入状态(0未录入,1已录入)
    typist_user = fields.ForeignKeyAcrossDB(User,db_column='typist_user',default=0)
    typist_time = models.DateTimeField(u'录入时间',auto_now_add = True) 

    class Meta:
        db_table='mis_upgrade_voucher'

class UpgradeVoucherProxy(UpgradeVoucher):
    def save_voucher(self,voucher=None):
        '''
        保存一个凭证信息
        '''
        dbInfo = None
        try:
            dbInfo = UpgradeVoucher.objects.get(user_id=voucher.user_id,
                                                cert_type = voucher.cert_type,
                                                name = voucher.name,
                                                apply_level = voucher.apply_level)
        except ObjectDoesNotExist:
            pass

        if dbInfo is None:
            dbInfo = UpgradeVoucher()
        
        dbInfo.user_id = voucher.user_id 
        dbInfo.cert_type = voucher.cert_type
        dbInfo.apply_level = voucher.apply_level
        dbInfo.name = voucher.name
        dbInfo.input_state = 0
        dbInfo.typist_user = 0
        
        dbInfo.save()
        return dbInfo.id

    def get_voucher(self,uid,name):
        '''
        根据一个用户uid和凭证name获取凭证
        '''
        try:
            return UpgradeVoucher.objects.get(user_id = uid,
                                              name = name)
        except Exception,e:
            return None
 
    class Meta:
        proxy = True

class ControlTable(models.Model):
    pass

class AuditLog(models.Model):
    id = models.AutoField(primary_key=True)
    ext_key = models.IntegerField(u'APPLYID或者UPgradeID',default=0) #这里显示ApplyID或者UpgradeID
    user_id = models.IntegerField(u'用户编码',default=0)
    apply_level = models.SmallIntegerField(u'要申请到的等级',default=0)
    type = models.SmallIntegerField(u'审核类型',default=2)  #类型：1注册审核2升级审核
    result = models.SmallIntegerField(u'审核结果',default=0)         #审核结果：1通过 0失败
    memo = models.CharField(u'备注',max_length=256) #备注
    groupid = models.IntegerField(u'渠道',default=10001,choices=GROUP_CHOICES)
    create_user = models.SmallIntegerField(u'创建人',default=0)
    create_date = models.DateTimeField(u'创建时间',auto_now_add=True)
    is_delete = models.SmallIntegerField(u'是否删除',default=0)

    class Meta:
        db_table = 'mis_auditlog'
        #app_label= u'useraudit'
        verbose_name_plural = u'审核日志'

    def display_type(self):
        if self.type == 1:
            return u'注册审批'
        elif self.type == 2:
            return u'升级审批'
        else:
            return '---'

    def display_result(self):
        if self.result == 1:
            return u'通过'
        elif self.result == 0:
            return u'失败'
        else:
            return '---'
    display_result.short_description = 'Result'

    def display_key(self):
        return self.ext_key
    display_key.short_description = 'UpId|ApplyId'

class VoucherConfirmInfo(models.Model):
    '''
    自动审核凭证对比差异表，录入信息和填写信息不一致的需要记录到此表，审核员手工确认哪个信息正确
    '''
    id = models.AutoField(primary_key=True)
    upgrade_id = models.ForeignKey(Upgrade,db_column='upgrade_id')
    user_id = models.IntegerField(u'用户编号')
    apply_level = models.SmallIntegerField(u'要申请的等级')
    cert_type = models.SmallIntegerField(u'凭证类型') #凭证类型,参阅util/define.py LICENSE_TYPE
    field = models.CharField(u'model的字段名称',max_length=64)  #model的字段名称
    desc = models.CharField(u'字段的描述信息',max_length=64) #字段的描述信息，如'姓名''营业执照号'
    input_value = models.CharField(u'输入的信息',max_length=256)
    typist_value = models.CharField(u'录入的信息',max_length=256)
    confirm_value = models.CharField(u'确认的信息',max_length=256)
    value_source = models.SmallIntegerField(u'信息来源',default=1) #1用户填写,2录入,3其他
    create_user = models.IntegerField(u'创建人',default=0)
    create_date = models.DateTimeField(u'创建时间',auto_now=True)
    state = models.SmallIntegerField(u'状态',default=0)
    is_delete = models.SmallIntegerField(u'是否删除',default=0)
     
    class Meta:
        #app_label = u'useraudit'
        db_tablespace=u'mis'
        verbose_name = u'凭证字段'
        verbose_name_plural = u'凭证字段审核结果'
        db_table = 'mis_voucher_confirminfo'

    def display_upgrade_id(self):
        return self.upgrade_id.id
    display_upgrade_id.short_description = 'UpgradeId'

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


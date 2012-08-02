#coding=utf-8

NextLevelAfterBasicLevel = 5

GROUP_CHOICES=(
    (10001,u'钱方直营'),
    (10002,u'山东渠道'),
    (10003,u'神码渠道'),
    (10004,u'北京电信'),
    (10005,u'天顺名扬'),
    (10006,u'脉动无限'),
    (10007,u'梦翔明日'),
    (10008,u'钱方测试'),
    (10009,u'北京京拍档'),
    (10010,u'沈阳新华银'),
    (10011,u'北京致远鸿图'),
    (10012,u'福州福铁'),
    (10013,u'南通杰盛'),
)

class GROUP_ID:
    '''渠道ID'''
    Qianfang = 10001
    Shandong = 10002
    Shenma   = 10003
    ChinaTelcom = 10004
    Tianshun = 10005
    Maidong = 10006
    Mengxiang = 10007
    QianfangTest = 10008
    Jingpaidang = 10009
    ShenyangXinhuayin = 10010
    Zhiyuanhongtu = 10011 
    Fuzhoufutie = 10012
    Nantongjiesheng = 10013

class TerminalUsedState:
    InWarehouse = 0 #入库
    AssignedPasm = 1      #已分配PSAM
    AssignedUser = 2       #已分配用户
    Logisticing = 3 #发货中
    Logisticed  = 4 #发货成功

class TerminalState:
    Normal = 0 #正常
    Fixing = 1 #维修中
    Rejected = 2 #报废

class PsamUsedState:
    InWarehouse = 0
    Assigned = 1
    OutWarehouse = 2

class PsamState:
    Normal = 0 #正常
    Fixing = 1 #维修中
    Rejected = 2 #报废

#账户类型
class AccountType:
    PRIME_TYPE = 0
    BASIC_TYPE = 1
    GOLD_TYPE = 2
    PLATINUM_TYPE = 3

    TypeDesc = [u'体验用户',u'基本用户',u'黄金用户',u'白金用户',u'----']
    @staticmethod
    def get_type_desc(user_level):
        '''
        10个level分4中类型，每个level对应的中文名称
        '''
        if user_level == 1:
            return u'体验级别'
        elif user_level >= 2 and user_level <=6:
            return u'基本级别'
        elif user_level >=7 and user_level <=10:
            return u'黄金级别'
        elif user_level > 10:
            return u'VIP级别'
        else:
            return u'神马级别'
    
    @staticmethod
    def get_level_type(user_level):
        '''
        10个level分4种类型，每个level对应的的大类别,暂时只用来显示页面用
        '''
        if user_level == 1:
            return AccountType.PRIME_TYPE
        elif user_level >= 2 and user_level <=6:
            return AccountType.BASIC_TYPE
        elif user_level >=7 and user_level <=10:
            return AccountType.GOLD_TYPE
        elif user_level > 10:
            return AccountType.PLATINUM_TYPE
        else:
            return -1


#用户账户的状态
AccountState = {
    1:'created',
    2:'passed',
    3:'active',
    4:'normal',
    5:'blocked',
    6:'blacklist',
    7:'canceled',
}

class ApplyState:
    '''
    Apply.State
    目前注册流程分多步，apply.state可以当做进度控制使用
    方便用户一次流程没有走完之后不能继续注册
    '''
    REGISTERED = 0 #已注册 step1
    COMMITINFO = 1 #已提交基本信息 step2
    UPLOAD_FILE =2 #已上传凭证 step3
    WAIT_AUDIT = 4 #等待审核 step4
    
    PASSED     = 5 #审核通过
    
    AUTO_AUDIT_FAILURE = 6 #自动审核失败
    AUDIT_FAILURE = 7 #人工审核失败
    WAIT_REAUDIT = 8 #等待复审

    @staticmethod
    def keys():
        return [0,1,2,3,4,5,6,7,8]

class UserState:
    '''
    UserState == AccountState
    '''
    
    CREATED = 1
    PASSED = 2
    ACTIVE = 3
    NORMAL = 4
    BLOCKED = 5
    BLACKLIST = 6
    CANCELED = 7

    TypeDesc = [u'',u'新建',u'审核通过',u'设备激活成功',u'正常',u'沉默',u'黑名单',u'销户']
    @staticmethod
    def get_type_desc(state):
        try:
            return UserState.TypeDesc[state]
        except:
            return '---'

#审核的状态
AuditState = {
   0:'registered',
   1:'applied',
   4:'waited',
   5:'passed'
}

#正则表达式模板
Patterns = {
    'mobile':'^0{0,1}(13[0-9]|14[0-9]|15[0-9]|18[0-9])[0-9]{8}$',
}
#购买类型
class BuyType:
    BUY_DEPOSITE = 1
    BUY_COD = 2
    SHENMA = 3

#用户类型
class UserType:
    PERSON = 1
    SPERSON = 2
    MERCHANT = 3
    CHANNEL = 10
    
    TypeDesc = ['---','个人','个体户','公司']
    @staticmethod
    def get_type_desc(type):
        return UserType.TypeDesc[type]



#全局分页设置
class PageSetting:
	PageSize = 10 #分页大小

#性别
GENDER_CHOICES = (
    ('1',u'男'),
    ('2',u'女'),
    ('3',u'其他'),
)

#民族
NATION_CHOICE=(

)    

class LICENSE_TYPE:
    '''
    证件类型(证件类型需要关联UPGRADE_IMAGE)
    一个证件可能关联多个image类型，身份证关联Upgrade_Image(1,2)
    '''
    #凭证类型
    ID_CARD = 1   #身份证*2
    TAX = 2       #税务登记证
    LICENSE = 3   #营业执照(到期日期（第一页）、年检章（第二页）)*2
    ORG_CODE = 4  #组织结构代码证
    CONTRACT = 5  #房屋租赁协议（房屋地址、到期日期、合同描述）*3
    GATHERING_REQUIRE_ATTEST = 6 #收款需求证明
    BUSINESS_ATTEST = 7 #营业证明照片(公司门面、公司环境、公司服务、公司外部轮廓)*7
    PAYED_TAX = 8 #完税证明
    LEGAL_PERSON_AUTH = 9 #法人授权书
    OTHER_VOUCHER = 10 #其他信用凭证（照片、合同）
    LEGAL_PERSON_ID_CARD = 11 #授权法人身份证*2
    CARDPHOTO = 12 #银行卡正反面
    APPLY_NUM_PHOTO = 13 #申请台数凭证
    OPEN_LICENSE = 14 #开户许可证复印件
    BUSINESS_CARD = 15 #商户名片

    SUPPORTED_IMAGE = ['.jpg','.jpeg','.png'];
    
    #凭证图片key=imagename,value=凭证类型
    IMAGE_TYPE = {'id_front':1,
                  'id_back':1,
                  'tax':2,
                  'license':3,
                  'license_page1':3,
                  'license_page2':3,
                  'org_code':4,
                  'contract':5,
                  'contract2':5,
                  'contract3':5,
                  'contract_address':5,
                  'contract_enddate':5,
                  'contract_desc':5,
                  'gathering_attest':6,
                  'business_attest_env':7,
                  'business_attest_srv':7,
                  'business_attest_aspect':7,
                  'business_attest_front':7,
                  'business_attest_other2':7,
                  'business_attest_other3':7,
                  'business_attest_other4':7,
                  'business_attest_other5':7,
                  'business_attest_other6':7,
                  'business_attest_other7':7,
                  'payed_tax':8,
                  'legal_person_auth':9,
                  'legal_person_auth_front':11,
                  'legal_person_auth_back':11,
                  'user_bank_card':12,
                  'apply_number':13,
                  'open_license':14,
                  'business_card':15,
                  'photo1':10,
                  'photo2':10,
                  'photo3':10,
                  'photo4':10,
                  'other_voucher':10}

    LC_FORM  = ['','IDCardInfoForm','TaxInfoForm','LicenseInfoForm','OrgcodeInfoForm','ContractInfoForm']
    
    @staticmethod
    def get_form_by_type(cert_type):
        '''
        凭证cert_type字段返回一个确定的ModelForm
        数据库里存的type是一个int，这个方法类似枚举的get_desc_by_value
        '''
        return LICENSE_TYPE.LC_FORM[cert_type]

class UPGRADE_STATE:
    WAIT_AUDIT = 0    #等待审核
    PASSED = 1        #审核通过
    AUTO_FAILURE = 2  #自动审核失败,等待人工审核
    REFUSED = 3       #拒绝
    APPLY = 9         #用户申请注册

class UPGRADE_SOURCE:
    '''
    升级方式
    '''
    WEB = 0 #已注册用户点击用户网站"升级"
    APPLY = 1 #用户注册

    ll = [u'网络申请',u'用户注册']
    @staticmethod
    def get_source_desc(t):
        try:
            return UPGRADE_SOURCE.ll[t]
        except:
            return '----'

class UPGRADE_IMAGE:
    '''
    升级表里的certtype字段
    每种类型代表前台页面的一个输入表单，id_front&id_back在前台页面就是一张表单
    '''
    
    STATE = {
        "WAIT_AUDIT":0,
        "PASSED":1,
        "UN_CLEAN":2,
        "UN_ELIGIBLE":3
    }

    #凭证上传成功后生产缩略图比例
    SIZE = {'SMALL' : (102,62),
            'MIDDLE': (450,214),
            'LARGE' : (1024,432)}

    #不同类型用户上传凭证的数量
    UPGRADE_COUNT_FOR_UPGRADE = {
        'USER_TYPE_1':2,
        'USER_TYPE_2':5,
        'USER_TYPE_3':6
    }


#!/usr/bin/env python
#coding=utf-8

import sys,os,time,pdb,logging,string
import mis_settings
from datetime import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = 'mis_settings'

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from audit.admin import pass_person,pass_sperson,pass_company 
from audit.models import Apply,AuditLog,Upgrade as _up,UpgradeVoucher as _upVoucher,UpgradeProxy as _upProxy,UpgradeVoucherProxy as _upVoucherProxy
from mis.models import IDCardInfo,LicenseInfo,TaxInfo,OrgcodeInfo,VoucherDataInfo,VoucherConfirmInfo
from core.models import Person,SPerson,Merchant
from util.define import UPGRADE_STATE,LICENSE_TYPE,UPGRADE_IMAGE

_logerror = logging.getLogger('auto_audit_error')
_loginfo = logging.getLogger('auto_audit_info')

#-----------服务启动-------------#
class AutoAuditService():
    def setup_django_settings(self):
        from django.core.management import setup_environ
        setup_environ(mis_settings)
        _loginfo.info('setup succeed!')

    def run(self):
        try:
            pid = os.fork()
        except OSError,e:
            print 'fork parent preocess error!'
            sys.exit(0)
        
        if pid == 0:
            print '-------------------------------------------'
            print 'auto_audit service start successed!#pid:%s'% os.getpid()
            print '-------------------------------------------'
        elif pid > 0:
            sys.exit(0)
        else:
            print 'fock process error!'
            sys.exit(0)

        count = 1
        f = open('logs/auto_audit.log','w')
        while True:
            f.write('#count:%s,pid:%s\r\n' % (count,os.getpid()))
            f.flush()
            count += 1

            _loginfo.info('************************************************pid:%s' % os.getpid())
            aplAudit = ApplyAutoAudit()
            aplAudit.start()
            _loginfo.info('------------------------------------------------')
            upAudit = UpgradeAutoAudit()
            upAudit.start()
            _loginfo.info('************************************************')
                
            time.sleep(180)

#-----------服务启动end-------------#

#-----------注册审核----------------#
class ApplyAuditBase():
    '''
    用户申请审批基类，集成此类的subclass需要重写valid函数，返回数据类型boolean！
    '''
    def _required(self,tupleList):
        result = True

        if len(tupleList) < 1:
            result = False
        
        for t in tupleList:
            if t['value'] is None or len(t['value']) == 0:
                self.msg.append(t['key'])
                result = False

        return result

    def __init__(self,apply):
        self.apply = apply
        self.valid_result = False
        self.valided = False
        self.msg = []
    
    def is_valid(self):
        if not self.valided:
            self.valid_result = self.valid()
            self.log()
            self.valided = True

        return self.valid_result

    def valid(self):
        '''
        子类需要重新此方法验证每个upgrad的信息是否通过！
        返回类型boolean
        '''
        raise Exception('not implemention!subclass must be rewrite this method!')
    
    def do_pass(self):
        '''
        这里用了wkz手动审核的那个action代码
        每个子类需要重写这个方法以实现自己的审批逻辑
        '''
        raise Exception('not implemention!subclass must be rewrite this method!')

    def do_failure(self):
        '''
        自动审核失败，需要进行人工审核，将Apply.State设置为6自动给审核失败，待人工确认
        '''
        try:
            _loginfo.info(u'apply audit failured !!!uid:%s,name:%s,type:%s' % (self.apply.user,self.apply.name,self.apply.usertype))
            _loginfo.info(u'required fields [%s]' % string.join(self.msg,sep=','))
        except Exception,e:
            _logerror.exception(e)

        apply = self.apply
        apply.state = 6 
        apply.save()

    def log(self):
        log = AuditLog(user_id=self.apply.pk,
                       ext_key = 0,
                       apply_level = 0, #需要修改，注册申请等级是否只能从最低级别开始？
                       type   = 1,
                       result = self.valid_result and 1 or 0,
                       memo   = self.valid_result and u'用户注册-自动审核-通过' or string.join(self.msg,sep=',')
                       ) 
        log.save()

class PersonApplyAudit(ApplyAuditBase):
    '''
    个人用户申请检查项目：姓名、身份证号、个人账户、开户银行
    '''

    def valid(self):
        if self._required([{'key':'name','value':self.apply.name},
                                  {'key':'idnumber','value':self.apply.idnumber},
                                  {'key':'bankname','value':self.apply.bankname},
                                  {'key':'bankaccount','value':self.apply.bankaccount}]):
            return True
        else:
            return False
    
    def do_pass(self):
        '''
        个人申请审核通过后执行的方法，pass_person封装不够全面需要手动把apply表的状态置为6！
        '''
        _loginfo.info('person apply passed!!!uid:%s,name:%s,type:%s' % (self.apply.user,self.apply.name,self.apply.usertype))
        
        pass_person(0,self.apply)
        self.apply.state = 5
        self.apply.save()
        
class SpersonApplyAudit(ApplyAuditBase):
    '''
    个体户用户申请检查项目：字号、经营地址、执照号、经营者姓名、经营者身份证号、经营者个人账户、开户银行
    '''
    def valid(self):
        if self._required([
                                 {'key':'name','value':self.apply.name},
                                 {'key':'businessaddr','value':self.apply.businessaddr},
                                 {'key':'linensenumber','value':self.apply.licensenumber},
                                 {'key':'contact','value':self.apply.contact},
                                 {'key':'idnumber','value':self.apply.idnumber},
                                 {'key':'bankname','value':self.apply.bankname},
                                 {'key':'bankaccount','value':self.apply.bankaccount}
                                 ]):
            return True
        else:
            return False
    
    def do_pass(self):
        '''
        个体户申请审核通过后执行的方法，pass_person封装不够全面需要手动把apply表的状态置为6！
        '''
        
        _loginfo.info('person apply passed!!!uid:%s,name:%s,type:%s' % (self.apply.user,self.apply.name,self.apply.usertype))

        pass_sperson(0,self.apply)
        self.apply.state = 5
        self.apply.save()

class MerchantApplyAudit(ApplyAuditBase):
    '''
    公司用户申请检查项目：企业注册名称、注册地址、执照号、法人姓名、法人身份证号、对公银行账户、开户银行
    '''
    def valid(self):
        if self._required([
                                  {'key':'name','value':self.apply.name},
                                  {'key':'businessaddr','value':self.apply.businessaddr},
                                  {'key':'licensenumber','value':self.apply.licensenumber},
                                  {'key':'legalperson','value':self.apply.legalperson},
                                  {'key':'idnumber','value':self.apply.idnumber},
                                  {'key':'bankname','value':self.apply.bankname},
                                  {'key':'bankaccount','value':self.apply.bankaccount}
                                  ]):
            return True
        else:
            return False
    
    def do_pass(self):
        '''
        个人申请审核通过后执行的方法，pass_person封装不够全面需要手动把apply表的状态置为6！
        '''
        _loginfo.info('person apply passed!!!uid:%s,name:%s,type:%s' % (self.apply.user,self.apply.name,self.apply.usertype))

        pass_company(0,self.apply)
        self.apply.state = 5
        self.apply.save()

class ApplyAutoAudit:
    '''
    用户申请自动审核
    '''
    APPLY_AUDITOR = {'AUDITOR_TYPE_1':PersonApplyAudit,
                     'AUDITOR_TYPE_2':SpersonApplyAudit,
                     'AUDITOR_TYPE_3':MerchantApplyAudit}

    def start(self):
        try:
            applyList = Apply.objects.filter(state=4)
            _loginfo.info('------------apply audit start!! applyCount=%s' % len(applyList))
            for apl in applyList:
                try:
                    auditor = self.APPLY_AUDITOR.get('AUDITOR_TYPE_'+str(apl.usertype))(apl)
                    if auditor.is_valid(): 
                        auditor.do_pass()
                        _loginfo.info('[apply_pass]:uid:%s,usertype:%s' % (apl.user,apl.usertype))
                    else:
                        _loginfo.info('[apply_failure]:uid:%s,usertype:%s' % (apl.user,apl.usertype))
                        auditor.do_failure()
                except Exception,e:
                    _loginfo.info(u'用户审核程序异常,apl.id:%s' % apl.user)
                    _logerror.exception(e)
        except Exception,e:
            _logerror.exception(e)
        finally:
            _loginfo.info('apply audit end!!')

#-----------注册审核END----------------#

#-----------升级审核-------------------#
#UpgradeAuditBase
class UpgradeAuditBase:
    '''
    用户升级自动审批基类
    '''
    #身份证对比字段''
    idcard = {
                Person:[('username','name',u'姓名',),('id_number','idNumber',u'身份证号',)],
                SPerson:[('legal_person','name',u'法人姓名',),('id_number','idNumber',u'法人身份证号')],
                Merchant:[('legal_person','name',u'法人姓名',),('id_number','idNumber',u'法人身份证号',)]
    }
    #营业执照
    license = {
                Person:[],
                SPerson:[('company','name',u'商户名称',),('license_number','number',u'营业执照编号'),('business_addr','address',u'商户地址'),('legal_person','legal_person',u'企业法人')],
                Merchant:[('company','name',u'商户名称',),('license_number','number',u'营业执照编号'),('business_addr','address',u'商户地址'),('legal_person','legal_person',u'企业法人')]
    }

    #税务登记证
    tax = {
            Person:[],
            SPerson:[('mcc','scope',u'法人姓名')],
            Merchant:[('mcc','scope',u'法人姓名')]
    }

    #组织结构代码证
    orgcode = {
                Person:[],
                SPerson:[('orgcode','orgcode',u'组织结构代码',)],
                Merchant:[('orgcode','orgcode',u'组织结构代码',)]
    }

    condition = {
                    'LICENSE_TYPE_1':idcard,
                    'LICENSE_TYPE_2':tax,
                    'LICENSE_TYPE_3':license,
                    'LICENSE_TYPE_4':orgcode
    }

    def _Voucher_Valid(self,xuser,upgrade):
        '''
        具体的凭证审核对比算法
        #1.查询upgrade关联的所有voucher
        #2.审核voucher信息
        #3.记录审核结果
        '''
        #pdb.set_trace()
        if xuser is None:
            raise Exception(u'凭证对比-用户异常,uid:%s' % upgrade.user_id)
        voucherList = _upVoucher.objects.filter(upgrade_id=upgrade,state=UPGRADE_STATE.WAIT_AUDIT)
        auditVoucherResult = {}

        for voucher in voucherList:
            voucherKey = 'LICENSE_TYPE_'+str(voucher.cert_type)
            
            if voucherKey not in self.condition.keys():
                continue;
            if voucherKey not in auditVoucherResult.keys():
                toCompareFields  = self.condition.get(voucherKey,{}).get(xuser.__class__,None)
                voucherInfo = VoucherDataInfo.objects.get_a_voucher(user_id=xuser.user.id,
                                                                    license_type=voucher.cert_type)
                
                VoucherConfirmInfo.objects.filter(user_id = xuser.user.id,
                                                  apply_level = upgrade.apply_level,
                                                  cert_type = voucher.cert_type)\
                                          .delete()

                result = True
                for fields in toCompareFields:
                    inputValue,typistValue = getattr(xuser,fields[0]),voucherInfo.get('fields').get(fields[1])
                    
                    if inputValue != typistValue: #如果信息不一致，需要把不一致的字段和信息写入VoucherComfirmInfo表，待人工审核
                        result = False

                        toConfirmField = VoucherConfirmInfo(
                                user_id = xuser.user.id,
                                apply_level = upgrade.apply_level,
                                upgrade_id = upgrade,
                                cert_type = voucher.cert_type,
                                field = fields[0],
                                desc = fields[2],
                                input_value = inputValue,
                                typist_value = typistValue
                        )

                        toConfirmField.save()
                        if toConfirmField.id is None or toConfirmField.id <= 0:
                            _logerror.error(u'凭证对比-保存结果异常,upgrade_id:%s,uid:%s,cert_type:%s,fild:%s' % (upgrade.id,upgrade.user_id,voucher.cert_type,fileds[0]))

                auditVoucherResult[voucherKey] = result
                self.msg.append(u'[%s:%s]' % (voucherKey,result))
            
            voucher.state = UPGRADE_STATE.PASSED and auditVoucherResult[voucherKey] or UPGRADE_STATE.AUTO_FAILURE
            voucher.save()

        if len(auditVoucherResult) > 0:
            isPassed = True
            for key in auditVoucherResult.keys():
                if not auditVoucherResult[key]:
                    isPassed = False
                    break
            return isPassed
        else:
            raise Exception(u'voucher_valid_error:凭证对比结果丢失!')

    def __init__(self,user,upgrade = None):
        self.user = user
        self.upgrade = upgrade
        self.is_valided = False
        self.is_valid_result = False
        self.msg = []

    def is_valid(self):
        if not self.is_valided:
            self.is_valided = True
            self.is_valid_result = self.valid()
            self.log()

        return self.is_valid_result
    
    def log(self):
        log = AuditLog(user_id=self.user.id,
                       ext_key = self.upgrade.id,
                       apply_level = self.upgrade.apply_level, #当前等级非要升级的等级！
                       result = self.is_valid_result and 1 or 0,#1通过0失败
                       memo   = u'用户升级-自动审核-UpgradeID:%s,Msg:%s' % (self.upgrade.id,string.join(self.msg,sep=','))
                       ) 
        log.save()
        _loginfo.info(string.join(self.msg,sep=','))
    
    def valid(self):
        raise Exception('subclass mast rewrite this method!valid()')

    def do_pass(self):
        '''
        审核通过，更新upgrade和user.user_level
        '''
        self.upgrade.state = UPGRADE_STATE.PASSWORD
        self.upgrade.auditor = 0
        self.upgrade.audittime = datetime.now()
        self.upgrade.memo = u'自动审核通过。'
        self.upgrade.save()
        self.user.user_level = self.upgrade.apply_level;
        self.user.save()
    
    def do_failure(self):
        '''
        如果一个凭证审核失败，需要把upgrade表的凭证信息置为自动审核失败，然后人工确认
        '''
        self.upgrade.state = UPGRADE_STATE.AUTO_FAILURE
        self.upgrade.auditor = 0
        self.upgrade.audittime = datetime.now()
        self.upgrade.memo = u'自动审核失败。'
        self.upgrade.save()

class PersonUpgradeAudit(UpgradeAuditBase):
    '''
    自动审核---用户升级审批
    '''
    def valid(self):
        '''
        个人用户升级审核，每个用户升级会在upgrade表里录入n张凭证
        验证录入员录入的凭证信息和person表是否一致，一致通过，不一致待人工审核
        '''
        person = None
        try:
            person = Person.objects.get(user__id=self.user.id)
        except ObjectDoesNotExist:
            _logerror.error('person not exist,uid=%s',self.user.id)

        return self._Voucher_Valid(person,self.upgrade)

class SpersonUpgradeAudit(UpgradeAuditBase):
    '''
    自动审核---个体户升级审批
    '''
    def valid(self):
        '''
        个体户用户升级审核，每个用户升级会在upgrade表里录入n张凭证
        验证录入员录入的凭证信息和sperson表是否一致，一致通过，不一致待人工审核
        '''
        sperson = None
        try:
            sperson = SPerson.objects.get(user__id=self.user.id)
        except ObjectDoesNotExist:
            _logerror.error('sperson not exist,uid=%s',self.user.id)
        
        return self._Voucher_Valid(sperson,self.upgrade)

class MerchantUpgradeAudit(UpgradeAuditBase):
    '''
    自动审核---公司升级审批
    '''
    def valid(self):
        '''
        公司用户升级审核，每个用户升级会在upgrade表里录入n张凭证
        验证录入员录入的凭证信息和sperson表是否一致，一致通过，不一致待人工审核
        '''
        merchant = None
        try:
            merchant = Merchant.objects.get(user__id=self.user.id)
        except ObjectDoesNotExist:
            _logerror.error('merchant not exist,uid=%s',self.user.id)

        return self._Voucher_Valid(merchant,self.upgrade)
    
class UpgradeAutoAudit:
    '''
    用户升级自动审核
    '''

    UPGRADE_AUDITOR = {'Auditor_Type_1':PersonUpgradeAudit,
                       'Auditor_Type_2':SpersonUpgradeAudit,
                       'Auditor_Type_3':MerchantUpgradeAudit}
    def start(self):
        try:
            #获取10个凭证审核请求，凭证只包括（身份证|营业执照|税务登记证|组织结构代码证）
            upProxy = _upProxy()
            uplist = upProxy.get_auto_audit_up() 
            _loginfo.info('------------------upgrade audit start!!counter:%s'% len(uplist))
            
            for upinfo in uplist:
                u = User.objects.get(pk=upinfo.user_id)
                #pdb.set_trace()
                upAuditor = self.UPGRADE_AUDITOR.get('Auditor_Type_'+str(u.user_type))(u,upinfo)
                
                if upAuditor.is_valid():
                    upAuditor.do_pass()
                    _loginfo.info('[upgrade_pass]:uid:%s,level:%s',upinfo.user_id,upinfo.apply_level)
                else:
                    _loginfo.info('[upgrade_failure]:uid:%s,level:%s',upinfo.user_id,upinfo.apply_level)
                    upAuditor.do_failure()
        except Exception,e:
            _logerror.exception(e)
        finally:
            _loginfo.info('upgrade audit end!!!')

if __name__ == '__main__':
    service = AutoAuditService()
    service.setup_django_settings()
    service.run() 

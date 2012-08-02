# coding: utf-8

import sys, os,pdb
import urllib,urllib2
import types

from django.core.mail import send_mail

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from settings import SERVER_EMAIL
from util.genpy.qfpay import SmsControl

def sendsms(to,content):
    return sendsmsv2(to,content)

def sendmail(tolist,subject,content):
    '''
    @tolist = ['a@mail.com','b@mail.com',]
    '''
    return send_mail(subject,content,SERVER_EMAIL,tolist,fail_silently=True)
    

SMS_SERVICE_IP = '192.168.10.11'
SMS_SERVICE_PORT = 5100

import logging
_LOG = logging.getLogger('mis_info')

def sendsmsv2(to,content):
    '''
    测试通过，切换到新网关
    Thrift接口返回值说明：
    ok:进入发送短信对列
    false:进入发送短对列失败
    -10:电话列表过多，最多100个电话
    -20:内容，内容过多长;最长700个字符
    '''
    if type(content) == types.UnicodeType:
        content = content.encode('utf-8')
 
    result = None
    try:
        transport = TSocket.TSocket(SMS_SERVICE_IP,SMS_SERVICE_PORT)
        TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        
        client = SmsControl.Client(protocol)
        transport.open()

        result = client.sendsms2('',to,content,'')
        _LOG.info('send sms to:%s,content:%s:,result:%s'%(to,content,result))
    except Exception,ex:
        _LOG.exception(ex)

    return result

if __name__ == "__main__":
    print sendsmsv2('18600360360',u'只是一个测试而已')

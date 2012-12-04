#!/usr/bin/env python
#-*-coding=utf-8-*-

import os
import sys
import platform
import json
import time
import commands

try:
    import pexpect
except:
    '''
    pexpect is intened for a unix-like operating system.
    '''
    print 'pexpect has ignore'
    pass

import log
LOG = log.getLogger('API')

from bottle import route, request

SUCCEED = 1
FAILED = 0

@route("/")
def index():
    return "EAYUN VM TOOLS V1.0.0.1"

@route("/action",method=['POST','GET'])
def action(): 
    '''
    EAYUN VM TOOLS API INTERFACE
    ALL OPERATION MUST BE CHECK IN BY THIS API
    '''
    succeed, msg = FAILED, 'HTTP POST ONLY'
     
    if request.method == 'POST':
        body = json.loads(request.body.readlines()[0])
        _action = body.get('action',None)
        if _action:
            _action = ACTION_MAPPER.get(_action,None)
            try: succeed, msg = _action(body)
            except Exception,ex:
                msg = ex.message
        else:
            msg = 'ACTION [%s] NOT IMPLENMENTION AT [%s]' % (_action, platform.system())
        
    result = {
        'SUCCEED' : succeed,
        'MESSAGE' : msg,
    }
    return result

def set_admin_password(body):
    '''
    request.POST:
    {
        "action" : "set_admin_password",
        "changePassword" : {
            "admin" : "root"
            "adminPass" : "ss1293837$%^"
        }
    }
    return (SUCCEED,MESSAGE)
    '''
    system = platform.system().lower()
    params = body.get('changePassword',{})
    user, password = params.get('admin',None), params.get('adminPass',None) 
    
    if user is None or password is None:
        return  FAILED,'user or password is none'

    if system == 'windows':
        return _windows_set_admin_password(user, password)
    else:
        return _linux_set_admin_password(user, password)

def _windows_set_admin_password(user,password):
    ''' 
    return (SUCCEED,MESSAGE)
    '''
    cmd = 'net user %s %s' % (user, password)
    #code, response = commands.getstatusoutput(cmd) 
    
    pipe = os.popen(cmd + ' 2>&1', 'r')
    response = pipe.read()
    code = pipe.close()
    if code is None: 
        code = 0
    
    if response[-1:] == '\n': 
        response = response[:-1]
    
    LOG.info('[set_admin_password]', response)

    try:response = response.decode('gbk').encode('utf-8').decode('utf-8')
    except:response = '-----'
    
    if code == 0:
        return SUCCEED, 'RESET PASSWORD SUCCEED AT WINDOWS'
    else:
        return FAILED, response

def _linux_set_admin_password(user,password):
    '''    
    return (SUCCEED,MESSAGE)
    '''
    child = pexpect.spawn("/usr/bin/passwd %s" % user) 
    logfile = os.path.normpath(os.path.join(os.path.abspath(__file__),os.path.pardir, os.path.pardir,'tools.log'))
    logfile =  open(logfile,'ab')
    child.logfile = logfile
 
    for repeat in (1, 2): 
        i = child.expect(["unix","password:",pexpect.EOF,pexpect.TIMEOUT],timeout=10)
        if i in [0,1]:
            child.sendline(password) 
            time.sleep(0.5)
        else:
            return SUCCEED, child.before
    
    LOG.info('[set_admin_password:Failed] %s %s' % (child.before,child.after))
    return FAILED,'%s %s' % (child.before,child.after)

ACTION_MAPPER = {
    "set_admin_password" : globals()['set_admin_password'],
}



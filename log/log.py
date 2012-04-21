#!/usr/bin/env python
#-*- coding=utf-8 -*-

import logging,datetime,time,pdb

def getLogger():
    now = datetime.datetime.now()
    
    logger = logging.getLogger('testApp')
    
    hdlr = logging.FileHandler(u'/home/zhanghui/pysharp/log/testapp_%s_%s.log'% (now.hour,now.minute))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)s %(message)s')
    hdlr.setFormatter(formatter)
    
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)

    return logger

if __name__=='__main__':
    _log = getLogger()
    #pdb.set_trace()
    while 1:
        try:
            r = 1/0
        except Exception,e:
            _log.exception(e)
        _log.info('--hello world!--')
        time.sleep(10)

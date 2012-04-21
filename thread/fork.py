#!/usr/bin/env python
# -*- coding=utf-8 -*-

'''a bssic fork in action'''

import sys,os,time

def my_fork():
    try:
        child_pid = os.fork()
    except OSError,e:
        print 'fork master precess failed:%d (%s)' % (e.errno,e.strerror)
        sys.exit(0)

    if child_pid == 0:
        print '-------------------------------------------'
        print 'auto_audit service start successed!#pid:%s'% os.getpid()
        print '-------------------------------------------'
    elif child_pid > 0:
        sys.exit(0)
    else:
        print 'fock process error!'
        sys.exit(0)

    count = 1
    f = open('fx.log','w')
    while 1:
        f.write('#count:%s,pid:%s\r\n' % (count,os.getpid()))
        f.flush()
        count += 1
        time.sleep(180)

if __name__ == '__main__':
    my_fork()

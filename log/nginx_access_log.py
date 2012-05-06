#!/bin/bash python
#-*- coding=utf-8 -*-

import re

'''
log_format combined '$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"

ip - - time path status_code content-length - agent

211.101.142.242 - - [07/Apr/2012:16:26:05 +0800] "-" 400 0 "-" "-"
211.101.142.242 - - [07/Apr/2012:16:26:07 +0800] "GET /login/?next=/ HTTP/1.1" 200 2641 "-" "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)"
'''

ACCESS_LOG_PATH = './access.log'
#ACCESS_LOG_PATH = './doc.log'

def test_readlines():
    '''测试readlines的耗时'''
    file  = open(ACCESS_LOG_PATH,'r')
    count = 0
    for line in file.readlines():
        count += 1
    print 'line:',count

def test_readline():
    '''测试readline的耗时'''
    file  = open(ACCESS_LOG_PATH,'r')
    count = 0
    while file.readline():
        count += 1

    print 'line:',count

def test_timeit():
    from timeit import Timer
    t1 = Timer("test_readlines()",setup='from __main__ import test_readlines;print "readlines test"')
    r1 = t1.timeit(5)
    print r1# * 1000
    
    t2 = Timer("test_readline()",setup='from __main__ import test_readline;print "readline test"')
    r2 = t2.timeit(5)
    print r2# * 1000    

def test_nginx_access_log_format():
    s = '211.101.142.242 - - [07/Apr/2012:16:26:07 +0800] "GET /login/?next=/ HTTP/1.1" 200 2641 "-" "Mozilla/5.0 (compatible; MSIE 9.0;     Windows NT 6.1; WOW64; Trident/5.0)"'
    
    print re.compile(r"(%(ip)s)\ -\ -\ (%(time)s)\ (%(path)s)\ (%(status)s)\ (%(length)s)\ (%(refer)s)\ (%(agent)s)" % {
            "ip"      : r"[\d.]*",
            "time"    : r"\[[^\[\]]*\]",
            "path"    : r"\"[^\"]*\"",
            "status"  : r"[\d]{3}",
            "length"  : r"\d+",
            "refer"   : r"\"[^\"]*\"",
            "agent"   : r"\"[^\"]*\""},re.VERBOSE).match(s).groups()


if __name__=='__main__':
    '''nginx access log analysis'''
    logPattern = re.compile(r"(%(ip)s)\ -\ (%(user)s)\ (%(time)s)\ (%(path)s)\ (%(status)s)\ (%(length)s)\ (%(refer)s)\ (%(agent)s)" % {
                        "ip"       : r"[\d.]*",
                        "user"     : r"[\w\W]*",
                        "time"     : r"\[[^\[\]]*\]", 
                        "path"     : r"\"[^\"]*\"", 
                        "status"   : r"[\d]{3}", 
                        "length"   : r"\d+", 
                        "refer"    : r"\"[^\"]*\"", 
                        "agent"    : r"\"[^\"]*\""}, re.VERBOSE)
    
    lc,m = 0,0
    
    _ip_dict = {}
    _status_dict = {}
    for line in open(ACCESS_LOG_PATH).readlines():
        lc += 1
        r = logPattern.match(line)
        if r:
            m += 1
            try:
                g = r.groups()

                _ip_dict.setdefault(g[0],0)
                _ip_dict[g[0]] += 1

                _status_dict.setdefault(g[4],0)
                _status_dict[g[4]] += 1
            except Exception,ex:
                print ex.message
        else:
            print line
            break

    print lc,m
    
    _status_dict = sorted(_status_dict.items(),key=lambda (k,v):(v,k),reverse=True)
    for k,v in _status_dict:
        print "%-3s : %5s" % (k,v)
    
    print '*'*30 
    
    _ip_dict = sorted(_ip_dict.items(),key=lambda (k,v):(v,k),reverse=True)
    for k,v in _ip_dict:
        print "%-15s : %5s" % (k,v)

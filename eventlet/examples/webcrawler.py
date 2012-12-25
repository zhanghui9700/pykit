#!/usr/bin/env python
#-*-coding=utf-8-*-

import eventlet
from eventlet.green import urllib2

urls = ["http://wwww.qq.com/", 
        "http://wwww.sina.com.cn/", 
        "http://www.sohu.com/"]

def fetch(url):
    print 'opening:', url
    body = urllib2.urlopen(url).read()
    print 'done with', url
    return url, body

pool = eventlet.GreenPool(200)
for url, body in pool.imap(fetch, urls):
    print 'got body form', url, 'of lengt', len(body)

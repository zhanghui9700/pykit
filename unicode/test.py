#!/usr/bin/env python
#-*-coding=utf=8-*-

import urllib,sys

if __name__=='__main__':
    if len(sys.argv) > 1:
        str = sys.argv[1]
        str = unicode(str,'gbk')
    else:
        str = '中文'

    print str
    params = {}
    params['name']=str.encode('UTF-8')
    params['key']='python.com'

    print urllib.urlencode(params)


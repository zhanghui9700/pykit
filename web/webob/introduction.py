#!/usr/bin/env python
#-*-coding=utf-8-*-

import pdb

from webob import Request
from pprint import pprint as p



environ = {
    'wsgi.url_scheme':'http',
    'HTTP_HOST':'localhost:80',
    'QUERY_STRING':'id=1&name=2',
}

#req = Request(environ)

req = Request.blank('/')
def application(environ,start_response):
    start_response('200 OK',[('Content-type','text/plain')])
    return ['Hello python!']

#(status_string,header_list,app_iter)
#res = req.call_application(application)

res = req.get_response(application)
print 'res:',type(res)
print 'status:',res.status
print 'headers:',res.headers
print 'body:',res.body
#pdb.set_trace()

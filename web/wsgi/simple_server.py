#!/usr/bin/env python
#-*-coding=utf-8-*-

import pprint as p

from wsgiref.simple_server import make_server

def hello_world_app(environ,start_response):
    p.pprint(environ)
    print '*'*30
    print start_response
    status = '200 OK'
    headers = [('Content-type','text/plain')]
    start_response(status,headers)

    return ["hello world"]

httpd = make_server('',11223,hello_world_app)
print 'Serving on port 11223...'

httpd.serve_forever()

#!/usr/bin/env python
#-*-coding=utf-8-*-

'''
simplest web app
def simple_app(environ,start_response):
    start_response('200 OK',[('Content-type','text/json')])
    return ['hello world']
'''

'''
using webob
from webob import Request,Response

def simple_app(environ,start_response):
    request = Request(environ)
    response = Response(body='hello world!',content_type='text/json')

    return response(environ,start_response)

'''

'''
routes
'''
from webob import Request,Response
from routes import Mapper

url_mapper = Mapper()

def dispath_app(environ,start_response):
    request = Request(environ)
    __import__('urls')
    matcher = url_mapper.match(request.path_info)
    callback = string_import(matcher['views'])
    response = Response(body=callback(request),content_type='text/plain')

    return response(environ,start_response)

def string_import(module_path):
    path,_sep,name = module_path(rpartition('.')
    _module = __import__(path,globals(),locals(),-1)

    return getattr(_module,name)


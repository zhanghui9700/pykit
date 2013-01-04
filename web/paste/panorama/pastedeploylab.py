#!/usr/bin/env python
#-*-coding=utf-8-*-

import os
import webob
import operator as op

from webob import Request
from webob import Response
from paste.deploy import loadapp
from wsgiref.simple_server import make_server


class LogFilter():
    '''filter'''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        print 'filter:LogFilter is called'
        return self.app(environ, start_response)

    @classmethod
    def factory(cls, global_conf, **kwargs):
        print 'in LogFilter.factory', global_conf, kwargs
        return LogFilter


class ShowVersion():
    ''''''
    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        start_response("200 OK", [("Content-type", "text/plain"),])
        return ["Paste Deploy LAB:version=1.0.0.", ]

    @classmethod
    def factory(cls, global_conf, **kwargs):
        print 'in ShowVersion.factory', global_conf, kwargs
        return ShowVersion()


class Calculator():

    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        req = Request(environ)
        res = Response()
        res.status = "200 OK"
        res.content_type = "text/plain"

        operator = req.GET.get("operator", None)
        operand1 = req.GET.get("operand1", None)
        operand2 = req.GET.get("operand2", None)

        print req.GET

        opnd1, opnd2 = int(operand1), int(operand2)

        result = op.__dict__[operator](opnd1, opnd2)

        res.body = "%s /n result=%d" % (str(req.GET), result)
        return res(environ, start_response)

    @classmethod
    def factory(cls, global_conf, **kwargs):
        print 'in calculator.factory', global_conf, kwargs
        return Calculator()


if __name__ == '__main__':
    '''# 假设在ini文件中, 某条pipeline的顺序是filter1, filter2, filter3

# app, 那么，最终运行的app_real是这样组织的：

app_real = filter1(filter2(filter3(app)))

# 在app真正被调用的过程中，filter1.__call__(environ,start_response)被首先调用，若某种检查未通过，filter1做出反应；否则交给filter2__call__(environ,start_response)进一步处理，若某种检查未通过，filter2做出反应，中断链条，否则交给filter3.__call__(environ,start_response)处理，若filter3的某种检查都通过了，最后交给app.__call__(environ,start_response)进行处理。
    '''
    config_path = "api-paste.ini"
    appname = 'ec2_api'
    wsgi_app = loadapp("config:%s" % os.path.abspath(config_path),
                        appname)
    server = make_server('localhost', 9700, wsgi_app)
    server.serve_forever()

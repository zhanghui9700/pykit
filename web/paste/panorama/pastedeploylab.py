#!/usr/bin/env python
#-*-coding=utf-8-*-

import os
import webob

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
        print 'in LogFilter.factory'
        print 'global_conf:', global_conf
        print 'kwargs:', kwargs
        return LogFilter

class ShowVersion():
    def __init__(self):
        pass



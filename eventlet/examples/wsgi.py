#!/usr/bin/env python
#-*-coding=utf-8-*-

import eventlet
from eventlet import wsgi

def index(env, start_response):
    if env['PATH_INFO'] != '/':
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found\r\n']

    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello, World\r\n']

wsgi.server(eventlet.listen(('', 9700)), index)

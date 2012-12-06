#!/usr/bin/env python
#-*-coding=utf-8-*-

MINIMAL_VERSION = "1.0"

def simple_app(environ,start_response):
    '''
    simple possibe application object
    '''
    status = '200 OK'
    response_headers = [
        ('Content-type','text/plain'),
    ]
    start_response(status,response_headers)
    return ['Hello world!\n','<hr/>','<h1>come form simple_app server</h1>']

class AppClass(object):
    '''
    Produce the same output, bug using a class

    Note: AppClass is the application here,so calling it
    return an instance of AppClase, which is then the iterable
    return value of the application callable as required by 
    the spec

    if we wanted to use "instance" of AppClass as application
    objects instead, we would have to implement a __call__
    method, which world be invoked to execute the application,
    and we would need to create an instance for use by the 
    server or gateway.
    '''

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

    def __iter__(self):
        status = '200 OK'
        response_headers = [
            ('Content-type','text/plain'),
        ]
        self.start_response(status,response_headers)
        yield "Hello world!\n"
        yield "<br />"
        yield "<h1>come from AppClass</h1>\n"

#not in PEP33, but mentioned in the comments to AppClass
class AlternateAppClass(object):
    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [
            ('Content-type','text/plain'),
        ]
        start_response(status, response_headers)
        
        return ['Hello world!\n','<hr/>','<h1>come form alternate app class server</h1>']

class MinimalMiddleware(object):
    '''
    bare-minimal, doesn't do anything at all, middleware.
    '''
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        return self.application(environ, start_response)

class SimpleMiddleware(object):
    '''
    Takes a prefix, and appends it to each line in the response.
    '''
    def __init__(self, application, prefix):
        self.application = application
        self.prefix = prefix

    def __call__(self, environ, start_response):
        response = self.application(environ, start_response)
        return ['%s %s' % (self.prefix, s) for s in response]

def main(global_config,**settings):
    '''
    settings comes from paste deploy, whatever values were in the section of the deployment config file
    '''
    print 'global_config:',global_config
    print 'settings:',settings

    if settings.get('use_class', False):
        return AppClass
    elif settings.get('use_alt_class', False):
        return AlternateAppClass()
    else:
        return simple_app

def middleware(global_config,**settings):
    prefix = settings.get("prefix","Booyeah:")

    def factory(app):
        return SimpleMiddleware(app,prefix)

    return factory

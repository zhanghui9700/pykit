#-*-coding=utf-8-*-

VERSION = 'v1.0'

# simple_app and AppClass are right out of PEP 333
def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world!\n']
    
class AppClass:
    """Produce the same output, but using a class

    (Note: 'AppClass' is the "application" here, so calling it
    returns an instance of 'AppClass', which is then the iterable
    return value of the "application callable" as required by
    the spec.

    If we wanted to use *instances* of 'AppClass' as application
    objects instead, we would have to implement a '__call__'
    method, which would be invoked to execute the application,
    and we would need to create an instance for use by the
    server or gateway.
    """

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

    def __iter__(self):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        self.start_response(status, response_headers)
        yield "Hello world!\n"

# not in PEP 333, but mentioned in the comments to AppClass
class AlternateAppClass:
    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['Hello world!\n']

class MinimalMiddleware:
    """
    Bare-minimum, doesn't do anything at all, middleware.
    """
    def __init__(self, application):
        self.application = application
        
    def __call__(self, environ, start_response):
        return self.application(environ, start_response)

class SimpleMiddleware:
    """
    Takes a prefix, and appends it to each line in the response.
    """
    def __init__(self, application, prefix):
        self.application = application
        self.prefix = prefix

    def __call__(self, environ, start_response):
        response = self.application(environ, start_response)
        return ['%s %s' % (self.prefix, s) for s in response]


def main(global_config, **settings):
    # settings comes from paste deploy, whatever values were in the section of the 
    # deployment config file
    if settings.get('use_class', False):
        return AppClass
    elif settings.get('use_alt_class', False):
        return AlternateAppClass()
    else:
        return simple_app

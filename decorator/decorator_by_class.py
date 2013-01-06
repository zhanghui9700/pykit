#!/usr/bin/env python
#-*-coding=utf-8-*-


class IdentityDecorator(object):
    def __init__(self, func):
        self.func = func

    def __call__(self):
        self.func()


@IdentityDecorator
def a_function():
    print "I'm a normal function."

a_function()
# >> I'm a normal function

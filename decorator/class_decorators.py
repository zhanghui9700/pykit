#!/usr/bin/env python
#-*-coding=utf-8-*-


foo = ['important', 'foo', 'stuff']


def add_foo(klass):
    klass.foo = foo
    return klass


@add_foo
class Person(object):
    pass

brian = Person()

print brian.foo
# >> ['important', 'foo', 'stuff']

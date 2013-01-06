#!/usr/bin/env python
#-*-coding=utf-8-*-


from functools import wraps

GLOBAL_NAME = "Brian"


def print_name(function=None, name=GLOBAL_NAME):
    def actual_decorator(function):
        @wraps(function)
        def returned_func(*args, **kwargs):
            print "My name is " + name
            return function(*args, **kwargs)
        return returned_func

    print 'function:', function

    if not function:  # User passed in a name argument
        def waiting_for_func(function):
            return actual_decorator(function)
        return waiting_for_func

    else:
        return actual_decorator(function)


@print_name
def a_function():
    print "I like that name!"


@print_name(name='Matt')
def another_function():
    print "Hey, that's new!"

a_function()
# >> My name is Brian
# >> I like that name!

another_function()
# >> My name is Matt
# >> Hey, that's new!

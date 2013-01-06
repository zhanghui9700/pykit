#!/usr/bin/env python
#-*-coding=utf-8-*-

#def logging_decorator(func):
#    def wrapper():
#        wrapper.count += 1
#        print "The function I modify has been called {0} times(s).".format(
#              wrapper.count)
#        func()
#    wrapper.count = 0
#    return wrapper


def logging_decorator(func):
    a = 0
    l = []
    def wrapper():
        print locals()
        print "The function I modify has been called {0} times(s).".format(
              count)
        l.append(1)
        print l
        func()
    count = 0
    b = 0
    return wrapper



def a_function():
    print "I'm a normal function."


modified_function = logging_decorator(a_function)

modified_function()
# >> The function I modify has been called 1 time(s).
# >> I'm a normal function.

modified_function()
# >> The function I modify has been called 2 time(s).
# >> I'm a normal function.

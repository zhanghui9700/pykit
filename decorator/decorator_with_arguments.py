#!/usr/bin/env python
#-*-coding=utf-8-*-


from functools import wraps


def argumentative_decorator(gift):
    def func_wrapper(func):
        @wraps(func)
        def returned_wrapper(*args, **kwargs):
            print "I don't like this " + gift + " you gave me!"
            return func(gift, *args, **kwargs)
        return returned_wrapper
    return func_wrapper


@argumentative_decorator("sweater")
def grateful_function(gift):
    print "I love the " + gift + "! Thank you!"

grateful_function()
# >> I don't like this sweater you gave me!
# >> I love the sweater! Thank you!


'''
Step by step:

The interpreter reaches the decorated function, compiles grateful_function, and binds it to the name 'grateful_function'.

argumentative_decorator is called, and passed the argument "sweater". It returns func_wrapper.

func_wrapper is invoked with grateful_function as an argument. func_wrapper returns returned_wrapper.

Finally, returned_wrapper is substituted for the original function, grateful_function, and is thus bound to the name 'grateful_function'.
'''

# If we tried to invoke without an argument:
# grateful_function = argumentative_function(grateful_function)

# But when given an argument, the pattern changes to:
# grateful_function = argumentative_decorator("sweater")(grateful_function)

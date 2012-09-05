#!/usr/bin/env python
#-*-coding=utf-8-*-

import functools
import time
from datetime import datetime

class memoized(object):
    def __init__(self,func):
        print '__init__:',func
        self.func = func
        self.cache = {}

    def __call__(self,*args):
        print '__call__:',self.func,'args:',args
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            return self.func(*args)

    def __repr__(self):
        return '[pukit]',self.func.__doc__

    def __get__(self,obj,objtype):
        
        print '__get__:',self.func
        return functools.partial(self.__call__,obj)

@memoized
def get_date(name=None):
    now = datetime.now()
    return '%s-%s-%s %s:%s:%s'%(now.year,now.month,now.day,now.hour,now.minute,now.second)

class Foo(object):
    def __init__(self):
        pass
    
    @memoized
    def test(self,name=None):
        now = datetime.now()
        return '%s-%s-%s %s:%s:%s'%(now.year,now.month,now.day,now.hour,now.minute,now.second)

if __name__ == '__main__':
    #f = Foo()

    #import pdb;pdb.set_trace()
    
    #print f.test('python')
    #time.sleep(1)
    #print f.test('c#')
    #time.sleep(1)
    #print f.test('python')
    
    #print '*'*30
    #print get_date('java')
    #time.sleep(1)
    #print get_date('ruby')

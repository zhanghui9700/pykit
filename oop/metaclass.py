#!/usr/bin/env python
#-*-coding=utf-8-*-

import sys

class MetaClass(type):
    def __init__(cls,name,bases,dict):
        #print '*'*20
        #print 'class:',cls
        #print 'name:',name
        #print 'bases:',bases
        #print 'dict:',dict
        #print '*'*20
        if not hasattr(cls,'previous'):
            cls.previous = []
        else:
            cls.previous.append(cls)

class OfTheDarkLord:
    __metaclass__ = MetaClass

class Ring(OfTheDarkLord):
    number = 9

class King(OfTheDarkLord):
    has_soul = False

class NormalA(object):
    pass

class NormalB(type):
    pass

class NormalC:
    pass

if __name__ == '__main__':
    ring = Ring()
    king = King()

    import pdb;pdb.set_trace()
    print 'it works!'

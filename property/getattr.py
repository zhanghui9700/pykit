#!/usr/bin/env python
# -*- coding=utf8 -*-

class Foo():
    
    def __init__(self,name):
        self.name = name

    def __getattr__(self,attrName):
        '''
        拦截“未定义”属性访问
        '''
        #print type(attrName)  #<type 'str'>
        print '__getattr__:%s' % attrName
        if attrName == 'age':
            return 2012
        else:
            raise AttributeError,attrName

    privateField = ['salary']
    def __setattr__(self,attrName,value):
        '''
        拦截“所有”属性定义
        '''
        if attrName not in self.privateField:
            self.__dict__[attrName] = value
        else:
            raise AttributeError,attrName

    def __getattribute__(self,attrName):
        '''
        拦截“所有”属性访问
        '''
        print  '__getattribute__:%s' % attrName
        if arrtName not in self.privateField:
            return self.__dict__[attrName]
        else:
            raise AttributeError,attrName
    
if __name__ == '__main__':
    fo = Foo('pysharp')
    #print dir(fo)
    #print fo.gender #raise an attribute error
    fo.age = 2011
    print 'undefined age:%s' % fo.age

    fo.salary = 99
    print 'property salay:%s' % fo.salary

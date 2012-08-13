#!/usr/bin/env python
#-*-coding=utf-8-*-

#tabstop=4 softtabstop=4 shiftwidth=4

'''
what is mixin?
In object-oriented programming languages, a mixin is a class that provides a certain functionality to be inherited or just reused by a subclass, while not meant for instantiation (the generation of objects of that class). Mixins are synonymous with abstract base classes. Inheriting from a mixin is not a form of specialization but is rather a means of collecting functionality. A class or object may “inherit” most or all of its functionality from one or more mixins, therefore mixins can be thought of as a mechanism of multiple inheritance.

简单的说, mixin 是一种类的多继承的机制.

什么时候需要 mixin ?
就如stackoveflow 上的回答, 有两个主要的使用 mixin 的场景:

你希望给一个类提供很多可选的特征(feature).
你希望在很多不同的类中使用一个特定的特征(feature).
'''

#A.传统方式实现mixin
class Base(object):
    pass

class FlyMixin(object):
    pass

class Bird(Base,FlyMixin):
    pass 

#B.通过闭包实现mixin
def _mixin(base,mixin,name):
    class MixinClass(base,mixin):
        pass
    MixinClass.__name__ = name
    return MixinClass

MyClass = _mixin(base,FlyMixin,"Airport")

#C.通过type动态构造类实现mixin
MyClass2 = type("UFO",(Base,FlyMixin),{})

#D.通过修改__bases__来实现mixin
#只能mixin classic class
class SuperBase(object):
    pass
class FuncMixin: #not inherite from object
    pass

SuperBase.__bases__ += (FuncMixin,)



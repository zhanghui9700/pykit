#!/usr/bin/env python
#-*-coding=utf-8-*-

#传统方式定义类
class Foo(object):
    A = 'i\'m string'
    def __init__(self,b=None):
        self.B = b

#metaclass方式动态定义类
Foo2 = type("Foo2",(object,),{"A":"hello world!"})
#上面我们通过type类的实例化来生成类A, 如果我们想自定义类的生成, 我们可以以type类为基 类派生出自定义的 metaclass.

def test_normal():
    f1 = Foo()
    f2 = Foo2()

    print 'Class Foo:',Foo
    print 'Class Foo2:',Foo2
    print 'f1=',f1,'f1.A=',f1.A
    print 'f2=',f2,'f2.A=',f2.A


#Meta.__new__是用来生成类A的类型对象, 我们可以在调用type.__new__之前更改 dictionary变量来增加/修改/删除新生成类A的成员变量/方法.
#Meta.__init__是在生成类A的类型对象后被调用类进行类A的初始化. 第一个参数cls 是已经生成的类A类型对象, 可以通过直接修改cls来修改类的定义, 例如增加成员变量.
#Meta.__call__是在生成类A的实例对象时被调用的, 通过调用type.__call__可以 生成该实例对象obj, 之后我们可以直接修改obj来实现实例对象的自定义.

class Meta(type):
    def __call__(self):
        print 'Enter Meta.__call__'
        obj = type.__call__(self)
        print 'Exit Meta.__call__'
        return obj

    def __new__(cls,name,bases,init_kwargs):
        print 'Enter Meta.__new__'
        type_new = type.__new__(cls,name,bases,init_kwargs)
        print 'Exit Meta.__new__'
        return type_new

    def __init__(cls,name,bases,init_kwargs):
        print 'Enter Meta.__init__'
        super(Meta,cls).__init__(name,bases,init_kwargs)
        print 'Exit Meta.__init__'

def test_my_meta():
    print 'create MetaFoo'
    MetaFoo = Meta('FooMeta',(object,),{"A":"hello meta!!!"})
    print 'Class MetaFoo:',MetaFoo
    print 'instance MetaFoo'
    f1 = MetaFoo()
    print 'f1=',f1,'f1.A=',f1.A

#Use Method 1
FooC = Meta('FooC',(object,),{"A":"hello meta!!!"})
#Use Method 2
class FooA(object):
    __metaclass__ = Meta #_FooA_metaclass
#Use Method 3
def meta_func(name,bases,kwargs):
    return type(name,bases,kwargs)
    
class FooB(object):
    __metaclass__ = meta_func

def test_use_meta():
    fc = FooC()
    fa = FooA()
    fb = FooB()
    print fc
    print fa
    print fb
    
if __name__ == '__main__':
    #test_normal()
    #test_my_meta()
    test_use_meta()

#使用 metaclass 的案例
#
#    动态修改类的方法和属性, 例如给方法增加decorator
#    类的序列化和反序列化
#    在生成类的时候进行接口检查和接口注册
#    对第三方库进行monkey patch
#    生成代理类
#    动态mixin
#    控制实例对象的生成, 例如单体实例, 监控所有生成的实例对象


#http://xiaocong.github.com/blog/2012/06/12/python-metaclass/

# -*- coding=utf-8 -*-
#source:http://www.ibm.com/developerworks/cn/linux/l-cpdecor.html
#

#典型的“旧时”classmethod
class C:
    def foo(cls,y):
        print "classmethod",cls,y
    foo = classmethod(foo)

#典型的“旧时”方法的转换
def enhanced(meth):
    def new(self,y):
        print "i am enhanced"
        return meth(self,y)
    return new

class D:
    def bar(self,x):
        print "some method says:",x
    bar = enhanced(bar)
#************************************#
'''
decorator所作的一切就是使您避免重复使用方法名
并且将decorator放在方法定义中第一处提及其名称的地方
'''
class E:
    @classmethod
    def foo(cls,y):
        print "classmethod",cls,y

    @enhanced
    def bar(self,x):
        print "some method says:",x

'''
Decorator只是一个语法糖，decorator其实就是一个至少具有一个参数函数----程序猿要负责确保decorator的返回内容仍然是一个有意义的函数或方法，并且实现了原函数为使链接有用而做的事情。
'''

#高级抽象

def arg_sayer(what):
    def what_sayer(meth):
        def new(self,*args,**kwargs):
            print what
            return meth(self,*args,**kwargs)
        return new
    return what_sayer

def FooMaker(word):
    class Foo(object):
        @arg_sayer(word)
        def say(self):
            pass
    return Foo()

#foo1 = FooMaker('this')
#foo2 = FooMaker('that')
#print type(foo1),;foo1.say()
#print type(foo2),;foo2.say()
'''
@arg_sayer()饶了很多弯路，但只获得非常有限的结果，不过对于它所阐明的几方面来说，这是值得的：
1.Foo.say（）方法对于不同实例有不同的行为。在这个例子来说，不同之处可能只是一个数值，可以轻松地通过其他方式改变这个值；不过原则上说，decorator可以根据运行时的决策来彻底重写这个方法。
2.本例中未修饰的Foo.say（）方法是一个简单的占位符。其整个行为都是decorator决定的。然后，在其他情况下，decorator可能会将未修饰的方法与一些新功能相结合。
3.Foo.say（）的修改是通过FooMaker类工厂在运行时严格确定的。更加典型的情况是在顶级定义类中使用decorator，这些类只依赖于编译时可用的条件。
4.decorator都是参数化的。或者更确切的说，arg_sayer（）本身根本就不是一个真正的decorator；arg_sayer（）所返回的函数--what_sayer（）就是一个使用了闭包来封装其数据的decorator函数。参数化的decorator比较常见，但是它们所需的函数嵌套为三层！
'''


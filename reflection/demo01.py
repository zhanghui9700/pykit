#-*- coding=utf-8 -*-

import sys
import inspect

def foo():pass

class Cat(object):
    def __init__(self,name='hello python'):
        self.name=name

    def say(self):
        print self.name

def test1_method_type():
    print 'method type'
    cat = Cat()
    print Cat.say #unbound method
    print cat.say #bound method

#2.访问对象的属性
def test2_property():
    print 'property'

    cat = Cat('python')
    print cat.name #python
    cat.say() #python

    print 'dir:',dir(cat) #method & property include base
    print '__dict__:',cat.__dict__ #instance property
    print 'vars:',vars(cat) #equral to __dict__

    if hasattr(cat,'name'):
        setattr(cat,'name','set_name_ed')
        print getattr(cat,'name') #set_name_ed

    getattr(cat,'say')() #set_name_ed
#3.模块
def test3_meta_module():
   import fnmatch as m
   print m.__doc__.splitlines()[0]
   print m.__name__ #fnmatch
   print m.__file__ #/usr/lib64/python2.6/fnmatch.pyc
   print m.__dict__.items()[0] #

#4.类
def test4_meta_class():
    print Cat.__doc__
    print Cat.__name__ #Cat
    print Cat.__module__ #__main__
    print Cat.__bases__ #(<type>,)
    print Cat.__dict__ #

#5.实例
def test5_instance():
    cat = Cat('python')
    print cat.__dict__ #name only property no method
    print cat.__class__ #Cat
    print cat.__class__ == Cat #True

def foo6():
    n = 1
    def _foo():
        print n
    n=2
    return _foo
def test6_function():
    '''
     __doc__: 函数的文档；另外也可以用属性名func_doc。
    __name__: 函数定义时的函数名；另外也可以用属性名func_name。
    *__module__: 包含该函数定义的模块名；同样注意，是模块名而不是模块对象。
    *__dict__: 函数的可用属性；另外也可以用属性名func_dict。
    不要忘了函数也是对象，可以使用函数.属性名访问属性（赋值时如果属性不存在将新增一个），或使用内置函数has/get/setattr()访问。不过，在函数中保存属性的意义并不大。
    func_defaults: 这个属性保存了函数的参数默认值元组；因为默认值总是靠后的参数才有，所以不使用字典的形式也是可以与参数对应上的。                    func_code: 这个属性指向一个该函数对应的code对象，code对象中定义了其他的一些特殊属性，将在下文中另外介绍。
    func_globals: 这个属性指向定义函数时的全局命名空间。
    *func_closure: 这个属性仅当函数是一个闭包时有效，指向一个保存了所引用到的外部函数的变量cell的元组，如果该函数不是一个内部函数，则始终为None。这个属性也是只读的。
    '''
    closure = foo6()
    print closure.func_closure
    print closure.func_closure[0].cell_contents

def test7_method():
    '''
    im_func: 使用这个属性可以拿到方法里实际的函数对象的引用。另外如果是2.6以上的版本，还可以使用属性名__func__。
    im_self: 如果是绑定的(bound)，则指向调用该方法的类（如果是类方法）或实例（如果是实例方法），否则为None。如果是2.6以上的版本，还可以使用属性名__self__。
    im_class: 实际调用该方法的类，或实际调用该方法的实例的类。注意不是方法的定义所在的类，如果有继承关系的话。 
    '''
    cat = Cat()
    im = cat.say
    print im.im_func
    print im.im_self
    print im.im_class

def test8_generator():
    '''
    __iter__: 仅仅是一个可迭代的标记。
    gi_code: 生成器对应的code对象。
    gi_frame: 生成器对应的frame对象。
    gi_running: 生成器函数是否在执行。生成器函数在yield以后、执行yield的下一行代码前处于frozen状态，此时这个属性的值为0。
    next|close|send|throw: 这是几个可调用的方法，并不包含元数据信息，如何使用可以查看生成器的相关文档。
    '''
    def gen():
        for n in xrange(10):
            yield n

    g = gen()
    print g #gernertor object
    print g.gi_code #code object
    print g.gi_frame #frame object
    print g.gi_running #0
    print g.next() #0
    print g.next() #1

    for n in g:
        print n

def test9_code():
    '''
    co_argcount: 普通参数的总数，不包括*参数和**参数。
    co_names: 所有的参数名（包括*参数和**参数）和局部变量名的元组。
    co_varnames: 所有的局部变量名的元组。
    co_filename: 源代码所在的文件名。
    co_flags:  这是一个数值，每一个二进制位都包含了特定信息。较关注的是0b100(0x4)和0b1000(0x8)，如果co_flags & 0b100 != 0，说明使用了*args参数；如果co_flags & 0b1000 != 0，说明使用了**kwargs参数。另外，如果co_flags & 0b100000(0x20) != 0，则说明这是一个生成器函数(generator function)。
    '''
    cat = Cat()
    co = cat.say.func_code
    print co.co_argcount #1
    print co.co_names #('name',)
    print co.co_varnames #('self',)
    print co.co_flags & 0b100 #0

def test10_frame():
    '''
    f_back: 调用栈的前一帧。
    f_code: 栈帧对应的code对象。
    f_locals: 用在当前栈帧时与内建函数locals()相同，但你可以先获取其他帧然后使用这个属性获取那个帧的locals()。
    f_globals: 用在当前栈帧时与内建函数globals()相同，但你可以先获取其他帧……。
    '''
    def add(x,y=1):
        f = inspect.currentframe()
        print f.f_locals #{y:1,x:2,f:frame}
        print f.f_back #frame
        return x+y
    add(2)

def test11_traceback():
    '''
    tb_next: 追踪的下一个追踪对象。
    tb_frame: 当前追踪对应的栈帧。
    tb_lineno: 当前追踪的行号
    '''
    def div(x,y):
        try:
            return x/y
        except:
            tb = sys.exc_info()[2]
            print tb #traceback object
            print tb.tb_lineno #154

    div(1,0)

if __name__ == '__main__':
    #test1_method_type()
    #test2_property()
    #test3_meta_module()
    #test4_meta_class()
    #test5_instance()
    #test6_function()
    #test7_method()
    #test8_generator()
    test9_code()
    test10_frame()
    test11_traceback()

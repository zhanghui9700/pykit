#-*- coding=utf8 -*-

def arg_sayer(what):
    def what_sayer(meth):
        def new(self,*args,**kwargs):
            print what
            return meth(self,*args,**kwargs)
        return new
    return what_sayer

def FooMaker(word=None):
    class Foo(object):
        @arg_sayer(word)
        def say(self):pass
    return Foo()

f1 = FooMaker('this')
f2 = FooMaker('that')

print type(f1),;f1.say()
print type(f2),;f2.say()
#print 'a',;print 'b',;print 'c',
#print 'd'

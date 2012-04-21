# coding=utf-8

class Foo(object):
    '''
    是否继承object是property能否生效的关键
    '''
    def __init__(self,name):
        self._name = name

    def getName(self):
        print 'get...'
        return self._name

    def setName(self,value):
        print 'set...'
        self._name = 'my name is %s' % value

    name = property(getName,setName,None,'hello property')

class EasyFoo(object):
    
    def __init__(self,name):
        self._name = name

    @property
    def name(self):
        print 'get...'
        return self._name

    @name.setter
    def name(self,name):
        print 'set ...'
        self._name = name

class Person: # Use (object) in 2.6
    def __init__(self, name):
        self._name = name
    
    def getName(self):
        print('fetch...')
        return self._name
    
    def setName(self, value):
        print('change...')
        self._name = value
    
    def delName(self):
        print('remove...')
        del self._name
    
    name = property(getName, setName, delName, "name property docs")

if __name__ == '__main__':
    fo = Foo('jack blue')
    print fo.name
    fo.name = 'kitty seven'
    print fo.name
    print fo.name.__doc__

    print '*'*20
    p = Person('frank backham')
    print p.name
    p.name = 'blark difu'
    print p.name
    print p.name.__doc__

    print '*'*20
    f = EasyFoo('hello python')
    print f.name
    f.name = 'i love csharp'
    print f.name

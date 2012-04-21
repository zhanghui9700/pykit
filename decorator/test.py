#coding=utf-8

import pdb,sys

def test_filter3(func):
    def wrap(*args):
        print 'wrapper3 works'
        return func(*args)
    return wrap


def test_filter2(func):
    def wrap(*args):
        print 'wrapper2 works'
        return func(*args)
    return wrap

def test_filter(prefix=None):
    def wrap(func):
        def __wrapper(*args,**kwargs):
            print prefix,'wrapper works!!'
            return func(*args,**kwargs)

        return __wrapper

    return wrap;

@test_filter2
@test_filter3
@test_filter(prefix='--')
def test():
    print 'test is works!'

if __name__ == '__main__':
    #test()

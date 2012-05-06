#!/bin/bash python
# -*- coding=utf-8 -*-

'''
http://www.velocityreviews.com/forums/t671713-python-dictionary-size-entry-limit.html
>> On a 32-bit system, the dictionary can have up to 2**31 slots,
>> meaning that the maximum number of keys is slightly smaller
>> (about 2**30).
>
> Which, in practice, means that the size is limited by the available memory.

Right. Each slot takes 12 bytes, so the storage for the slots alone
would consume all available address space.

From that point of view, you can't possibly have more than 314M slots
in a 32-bit address space (roughly 2**2.

'''
from timeit import Timer

LIST_LENGTH = 1000000

def test_list():
    lst = []
    for x in xrange(LIST_LENGTH):
        lst.append('hello python')

def test_list_preallocate():
    lst = [None] * LIST_LENGTH
    for x in xrange(LIST_LENGTH):
        lst[x] = 'hello python'

if __name__ == '__main__':
    t1 = Timer('test_list()',setup='from __main__ import test_list;print "test_list do..."')
    r1 = t1.timeit(10)/10
    print r1
    
    t2 = Timer('test_list_preallocate()',setup='from __main__ import test_list_preallocate;print "test_list_preallocate do..."')
    r2 = t2.timeit(10)/10
    print r2
     

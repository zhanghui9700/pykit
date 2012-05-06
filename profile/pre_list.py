#!/bin/bash python
# -*- coding=utf-8 -*-

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
     

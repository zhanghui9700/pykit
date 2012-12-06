#!/usr/bin/env python
#-*-coding=utf-8-*-

import time

def producer(l):
    i = 0
    while True:
        i += 1
        l.append(i)
        time.sleep(5)
        
        yield i

        if i > 5:
            break

def consumer(l):
    p = producer(l)
    while True:
        try:
            i = p.next()

            while len(l) > 0:
                print l
                print l.pop()
        except:
            print 'consumer send'
            p.send(None)

l = []

consumer(l)

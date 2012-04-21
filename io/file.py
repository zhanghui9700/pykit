#!/usr/bin/env python
# -*- coding=utf-8 -*-

import sys,os,time

def main():
    f = open('fx.log','a')#a,w,r
    print 'write!'
    f.write(u'------------------\r\n')
    f.flush()

if __name__=='__main__':
    main()

#!/bin/bash python
#-*- coding=utf-8 -*-

import pdb

def quicksort(ll,start,end):
    print 'TOP:%s,start=%s,end=%s'%(ll[start:end+1],start,end)
    key = ll[end]
    if start > end:
        return

    i,j,move_i = start,end,True
    
    while i < j:
        def swap(lst,i,j):
            tmp = lst[i]
            lst[i]=lst[j]
            lst[j]=tmp
        
        if move_i:
            if ll[i] > key:
                swap(ll,i,j)
                move_i = False
            else: 
                i += 1
        else:
            if ll[j] < key:
                swap(ll,i,j)
                move_i = True
            else:
                j -= 1
    
    #pdb.set_trace() 
    quicksort(ll,start,i-1)
    print '-'*30
    quicksort(ll,i+1,end)

if __name__=='__main__':
    ll = [8,2,3,7,1,5,4,6,9,5]
    print ll
    print '*'*30
    quicksort(ll,0,len(ll)-1)
    print ll
    
    def quick(l):
        if len(l) < 2:
            return l
        print [x for x in l if x<=l[0]]
        print [x for x in l if x > l[0]]
        return quick([x for x in l if x < l[0]]) + l[0:1] +quick([x for x in l if x > l[0]])

    #print ll

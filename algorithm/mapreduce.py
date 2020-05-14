#!/bin/bash python
#-*- coding=utf-8 -*-

import sys
from multiprocessing import Pool

def test_what_mapreduce():
    '''
    '''
    a = [1,2,3]
    b = [4,5,6,7]
    c = [8,9,1,2,3]

    L = map(lambda x :len(x),[a,b,c])
    print L #[3,4,5]

    N = reduce(lambda x,y:x+y,L)
    print N #12

    M =reduce(lambda x,y:x+y,map(lambda x :len(x),[a,b,c]))
    print M

def sanitize(w):
    '''
    if a token has been identified to contain
    non-aplhanumeric characters,such as punctuation,
    assume it is leading or trailing punctuation
    and trim them off.Other internal punctuation
    is left intact
    '''
    while len(w) > 0 and not w[0].isalnum():
        w = w[1:]

    while len(w) > 0 and not w[-1].isalnum():
        w = w[:-1]

    return w

def load(path):
    '''
    load the contents the file at the given
    path into a big string and return it.
    '''
    word_list = []
    f = open(path,'r')
    for line in f:
        word_list.append(line)

    return (''.join(word_list)).split()

def chunks(l,n):
    '''
    a generator function for chopping up a given lsit into chunks of length n
    '''
    for i in xrange(0,len(l),n):
        yield l[i,i+n]

def tuple_sort(a,b):
    '''
    sort tuples by term frequency,and then alphabetically
    '''
    if a[1] < b[1]:
        return 1
    elif a[1] > b[1]:
        return -1
    else:
        return cmp(a[0],b[0])

def Map(L):
    '''
    given a list of tokens,return a lsit of tuples of 
    titlecased (or proper noun) tokens and a count of '1'.
    also remove any leading or trailing punctuation from
    each token
    '''
    result = []
    for w in L:
        #True if w contains non-apphanumeric characters
        if not w.isalnum():
            w = sanitize(w)

        #True if w is a title-cased token
        if w.istitle():
            results.append((w,1))

    return result

def Partition(L):
    '''
    group the sublists of(token,1)pairs into a term-frequency-list
    map,so that the reduce operation later can work on sorted term
    counts.the returned result is a dictionary with the structure
    {token:[(token,1),...]...}
    '''
    tf = {}
    for sublist in L:
        for p in sublist:
            #Append the tuple to the list in the map
            try:
                tf[p[0]].append(p)
            except KeyError:
                tf[p[0]] = [p]

    return tf

def Reduce(Mapping):
    '''
    given a (token,[(token,1)...])tuple,collapse all the count
    tuples form the Map operation into a single term frequency
    number for this token,and return a final tuple(token,frequency).
    '''
    return (Mapping[0],sum(pair[1] for pair in Mapping[1]))

if __name__ == '__main__':
    #test_what_mapreduce()
    if (len(sys.argv) != 2):
        print 'program required path to file for reading!'
        sys.exit(1)

    #load file,stuff it into a string
    text = load(sys.argv[1])

    #build a pool of 8 processed
    pool = Pool(processes = 8,)

    #frament the string data into 8 chunks
    partitioned_text = list(chunks(text,len(text)/8))

    #generate count tuples for title-cased tokens
    single_count_tuples = pool.map(Map,partitioned_text)

    #organize the count tuples;lists of tuples by token key
    token_to_tuples = Partition(single_count_tuples)

    #collapse the lists of tuples into total term frequencies
    term_frequencies = pool.map(Reduce,token_to_tuples.items())

    #sort the term frequencies in nonincreasing order
    term_frequencies.sort(tuple_sort)

    for pair in term_frequencies[:20]:
        print pair[0],':',pair[1]

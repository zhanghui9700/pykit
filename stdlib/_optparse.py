#!/bin/bash python
#-*-coding=utf-8-*-

import pdb
from optparse import OptionParser

def main():
    parser = OptionParser(usage=u'usage %prog [options] filename',version='%prog 1.0')
    parser.add_option('-x','--xhtml',\
                      action='store_true',\
                      dest='xhtml_flag',\
                      default=False,\
                      help='create a xhtml template instead of HTML',)

    parser.add_option('-c','--cssfile',\
                      action='store',\
                      dest='cssfile',\
                      default='style.css',\
                      metavar='FILLE',\
                      help='css file to link',)

    parser.add_option('-e','--env',\
                      type='choice',\
                      dest='environment',\
                      choices=['linux','unix','windows'],\
                      default='linux',\
                      help='environment to run on',)

    (options,args) = parser.parse_args()
    #if len(args) != 1:
    #    parser.error('wrong number of arguments')
    
    #pdb.set_trace() 
    print options
    print args


if __name__ == '__main__':
    main()

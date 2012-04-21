#!/usr/bin/env python
#-*- coding=utf-8 -*-

import sys,os,Image as _img

def image_pig(imgfile,width,height):
    orig_img = _img.open(imgfile)
    orig_img.thumbnail([height,width],_img.ANTIALIAS)
    newName = u'%sx%s_%s' % (width,height,imgfile) 
    print newName
    orig_img.save(newName,orig_img.format,quality=100)
    
if __name__=='__main__':
    #for i in sys.argv[1:]:
    #    print '-%s-\r\n' % i
    if len(sys.argv) == 4:
        image_pig(sys.argv[1],sys.argv[2],sys.argv[3])
    else:
        print 'python pig_image.py filename width height'

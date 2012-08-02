#!/usr/bin/evn python
#coding=utf-8

import os,Image,pdb

from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import HttpResponse

from util.define import UPGRADE_IMAGE

SUPPORTED_IMG = ['.jpg','.jpeg','.png']


def remove_image(userid,cert_name):
    #pdb.set_trace()
    userid = int(userid)
    path = settings.MEDIA_ROOT+`userid`
    filename = u'%(path)s/%(name)s'%{'path':path,'name':cert_name}
    if os.path.isfile(filename):
        os.remove(filename)
        for key in UPGRADE_IMAGE.SIZE.keys():            
            name = u'%(path)s/%(scale)s_%(name)s' % {'path':path,'name':cert_name,'scale':key.lower()}
            if os.path.isfile(name):
                os.remove(name)
    return


def save_image(userid,cert_name,file):
    '''
    保存用户上传的图片，并生成缩略图
    缩略图small_xxx.jpg,middle_xxx.jpg,large_xxx.jpg
    userid=uid
    cert_name = 'id_front|id_back_tax'
    file = request.FILES[xxx]
    '''
    userid = int(userid)
    path = settings.MEDIA_ROOT+`userid` #path/10001(uid)/file
    if not os.path.exists(path):
        os.makedirs(path)

    ext = os.path.splitext(file.name)[1].lower()
    if ext not in SUPPORTED_IMG:
        raise Exception(u'imgstore.py not supported image,ext:%s,filename:%s' % (ext,file.name))
    
    ext = '.jpg'#统一修改一下文件扩展名
    orig_filename  = u'%(path)s/%(name)s%(ext)s'% {'path':path,'name':cert_name,'ext':ext}

    handle = open(orig_filename, 'wb+')
    for chunk in file.chunks():
        handle.write(chunk)
    handle.close()
   
    for key in UPGRADE_IMAGE.SIZE.keys():
        orgimg = Image.open(orig_filename)
        scale = orgimg.resize(UPGRADE_IMAGE.SIZE.get(key), Image.ANTIALIAS)
        name = u'%(path)s/%(scale)s_%(name)s%(ext)s' % {'path':path,'name':cert_name,'scale':key.lower(),'ext':ext}
        scale.save(name, orgimg.format, quality=100)
    
    return cert_name + '' + ext

def preview_img_response(uid,name,scale):
    '''
    userid = auth_user.id
    filename =  
    type = 'small|middle|large'
    '''
    uid = int(uid)
    path = settings.MEDIA_ROOT+`uid`
    if scale.lower() == 'original':
        path = path + '/' + name
    else:
        path = path + '/'+ scale +  '_' + name
    if not os.path.isfile(path):
        raise Exception(u'file not exist,file:%s' % path)

    img = Image.open(path)
    response = HttpResponse(mimetype='image/'+img.format)
    img.save(response, img.format)

    return response


def format_filename(filename, newname):
    ext = os.path.splitext(filename)[1]
    if ext=='':
        ext = '.jpg'
    orig_name = newname + ext
    small_img = newname + '_small'+ext
    
    return orig_name, small_img

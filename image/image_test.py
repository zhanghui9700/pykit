#coding=utf-8
import os,Image,pdb

class UPGRADE_IMAGE:
    '''
    升级表里的certtype字段
    每种类型代表前台页面的一个输入表单，id_front&id_back在前台页面就是一张表单
    '''
    #凭证上传成功后生产缩略图比例
    SIZE = {'SMALL' : (102,62),
            'MIDDLE': (450,214),
            'LARGE' : (1024,432)}

    #不同类型用户上传凭证的数量
    UPGRADE_COUNT_FOR_UPGRADE = {
        'USER_TYPE_1':2,
        'USER_TYPE_2':5,
        'USER_TYPE_3':6
    }




SUPPORTED_IMG = ['.jpg','.jpeg','.png']

def save_image():
    '''
    保存用户上传的图片，并生成缩略图
    缩略图small_xxx.jpg,middle_xxx.jpg,large_xxx.jpg
    userid=uid
    '''
    #pdb.set_trace()

    orig_filename  = u'Ner_ben.jpg'

   
    for key in UPGRADE_IMAGE.SIZE.keys():
        orgimg = Image.open(orig_filename)
        scale = orgimg.resize(UPGRADE_IMAGE.SIZE.get(key), Image.ANTIALIAS)
        name = u'%(scale)s.jpg' % {'scale':key.lower()} 
        scale.save(name, orgimg.format, quality=100)

if __name__=='__main__':
    save_image()

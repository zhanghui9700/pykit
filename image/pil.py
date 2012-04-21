#coding = utf-8

import sys,os,Image

rate = 200
resizedAddone = '_small'
supportFormat = ['.bmp','.jpg','.png']
SIZE = {'SMALL' : (102,62),
        'MIDDLE': (512,216),
        'LARGE' : (1024,432)}

def process(arg,dirs,files):
    for file in files:
        fileExt = os.path.splitext(file)[1].lower() 
        if fileExt in supportFormat:
            print 'img:',file
            img = Image.open(file)
            print img.size[0],img.size[1]
            
            for key in SIZE.keys():
                resize = img.resize(SIZE.get(key))
                resize.save(os.path.basename(file) + '_' + key + fileExt)

if __name__ == '__main__':
    print 'sys.argv[0]:',sys.argv[0]
    print 'os.getcwd():',os.getcwd()
    print 'abspath:',os.path.abspath(sys.argv[0])

    os.path.walk('.',process,'')

#!/bin/bash python
#-*- coding=utf-8 -*-

import os
from hashlib import sha256
from hmac import HAMC

def encrypt_passwd(passwd,salt=None):
    '''
    hash passwd on the fly
    这里先通过标准随机库生成 64 bits 的随机 salt，使用了标准的 SHA-256 做为基本的 hash 算法，使用标准 HMAC 算法作为 salt 混淆。并且进行了 10 次混淆 hash。最后将 salt 和 hash 结果一起返回。 
    '''
    if salt is None:
        salt = os.urandom(8)

    assert 8 == len(salt)
    assert isinstance(salt,str)

    if isistance(passwd,unicode):
        passwd = passwd.encode('UTF-8')

    assert instance(passwd,str)

    result = passwd

    for i in xrange(10):
        result = HAMC(result,salt,sha256).digest()

    return salt + result

def validate_passwd(hasded,input_passwd):
    return hasded == encrypt_passwd(input_passwd,salt=hashed[:8])

if __name__ == '__main__':
    pwd = '12345678'
    hashed = encrypt_passwd(pwd)
    print hashed

    '*'*20

    print validate_passwd(hashed,pwd)

    

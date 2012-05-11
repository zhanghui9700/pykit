#!/bin/bash python
# -*- coding=utf-8 -*-

import socket

END_POINT = ('127.0.0.1',9780)

if __name__ == '__main__':
    skt = socket.socket()
    
    skt.bind(END_POINT)
    skt.listen(2)
   
    while True:
        conn,address = skt.accept()
        print 'get connection form:',address

        conn.send('welcome,what u want:')
        recv = conn.recv(512)
        print '----'
        print recv
        
        conn.send('i dont kown too,hhahaha')

        conn.close()

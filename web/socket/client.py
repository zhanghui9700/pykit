#!/bin/bash python
# -*- coding=utf-8 -*-

import socket

END_POINT = ('127.0.0.1',9780)

if __name__ == '__main__':
    skt1 = socket.socket()
    skt1.connect(END_POINT)
    
    while True:
        data = skt1.recv(512)
        print data
        skt1.send(raw_input())
    

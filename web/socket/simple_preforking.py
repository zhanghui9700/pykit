#!/bin/bash python
#-*-coding=utf-8-*-

import pdb
import os,sys,socket

acceptor = socket.socket()
acceptor.bind(('localhost',9710))
acceptor.listen(2)

for i in range(3):
    pid = os.fork();
    
    if pid == 0:
        child_pid = os.getpid()
        print 'child %s listening on localhost:9710'%child_pid
        
        try:
            while True:
                conn,addr = acceptor.accept()
                
                flo = conn.makefile()
                flo.write('child %s echo>'%child_pid)
                flo.flush()
                
                #pdb.set_trace()
                
                message = flo.readline()
                flo.write(message)
                flo.flush()
                conn.close()

                print 'child %s echo\'d:%r'%(child_pid,message.strip())
        except KeyboardInterrupt:
            sys.exit()


try:
    os.waitpid(-1,0)
except KeyboardInterrupt:
    print '\nbailing'
    sys.exit()

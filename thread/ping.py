#-*- coding=utf-8 -*-

import os
import re
import time
import sys
from threading import Thread

lifeline = re.compile(r'(\d) received')
report = ('No response','Partial Response','Alive')

#**************************************
def single_thread_test():

    print time.ctime()
    
    for host in range(60,70):
        ip = '192.168.200.%s' % host
        pingaling = os.popen('ping -q -c2 '+ip,'r')
        print 'testing ip is:',ip,
        sys.stdout.flush()
        
        while 1:
            line = pingaling.readline()
            if not line:break
            igot = re.findall(lifeline,line)
            if igot:
                print report[int(igot[0])]
    
    print time.ctime()
#**************************************

class Job(Thread):
    def __init__(self,ip,sleep=0):
        Thread.__init__(self)
        self.ip = ip
        self.status = -1
        self.sleep = sleep

    def run(self):
        pingaling = os.popen('ping -q -c2 '+self.ip,'r')
        while 1:
            line = pingaling.readline()
            if not line:break
            igot = re.findall(lifeline,line)
            if igot:
                self.status = int(igot[0])
        
        time.sleep(self.sleep)

def multi_thread_test():
    print time.ctime()
    
    pinglist = []
    for host in range(1,11):
        ip = '172.100.101.%s' % host
        if host == 1:
            current = Job(ip,10)
        else:
            current = Job(ip)
        pinglist.append(current)
        current.start()

    for pingle in pinglist:
        pingle.join()
        print 'Status from ',pingle.ip,'is',report[pingle.status]
    
    print time.ctime()

#**************************************
if __name__ == '__main__':
    #single_thread_test()
    multi_thread_test()

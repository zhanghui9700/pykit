#!/usr/bin/env xpython
#-*-coding=utf-8-*-

import os
import signal
import time
import threading

def test_bind_signal():
    def onsignal_term(a, b):
        print 'reveive a signal: SIGTERM'

    #bind signal event callback
    signal.signal(signal.SIGTERM, onsignal_term)

    def onsignal_usr1(a, b):
        print 'receive a signal: SIGUSR1'

    signal.signal(signal.SIGUSR1, onsignal_usr1)

    while 1:
        print 'my process id is:', os.getpid()
        time.sleep(10)

def test_child_process_signal_parent():
    def onsigchild(a, b):
        print 'child received a signal: SIGCHLD'

    signal.signal(signal.SIGCHLD, onsigchild)
    print 'main process id: ', os.getpid()
    pid = os.fork()
    
    print 'fork pid: ', pid #this pid is child new process id or 0

    if pid == 0:
        print 'i\'m the child process, my process id is: ', os.getpid()
        time.sleep(5)
    else:
        print 'i\'m the parent process, my process id is: ', os.getpid()
        os.wait() #wait child process to complete.

def test_signal_alarm():
    def receive_alarm(signum, stack):
        print 'Alarm: ', time.ctime()

    signal.signal(signal.SIGALRM, receive_alarm)
    signal.alarm(2)

    print 'Before: ', time.ctime()
    time.sleep(10)
    print 'After: ', time.ctime()

def test_signal_thread():
    def signal_handler(num, stack):
        print 'Received signal %d in %s' % (num, threading.currentThread().name)

    signal.signal(signal.SIGUSR1,signal_handler)

    def wait_for_signal():
        '''only main thread can received the signal
        the 'Done waiting' msg will never print the terminal!!
        '''
        print 'Waiting for signal in: ', threading.currentThread().name
        signal.pause()
        print 'Done waiting'

    #Start a thread that will not receive the signal
    receiver = threading.Thread(target=wait_for_signal, name="receiver")
    receiver.start()
    time.sleep(1)
    
    def send_signal():
        print 'Sending signal in: ', threading.currentThread().name
        os.kill(os.getpid(), signal.SIGUSR1)

    sender = threading.Thread(target=send_signal, name="sender")
    sender.start()
    sender.join()

    #wait for the thread to see the signal (not going to happen!)
    print 'Wait for ', receiver.name
    signal.alarm(2) #if we comment this line the process will be blocked by the receiver thread! because receiver threade can\'t receive the signal!
    receiver.join()

def test_alarm_only_received_by_main_thread():
    '''虽然 alarms 类信号可以在任何线程中调用，但是只能在主线程中接收，像下面例子即使子线程 use_alarm 中调用  signal.alarm(1) ，但是不起作用
    '''
    def signal_handler(num, stack):
        print time.ctime(), 'Alarm in: ', threading.currentThread().name
    signal.signal(signal.SIGALRM, signal_handler)

    def use_alarm():
        t_name = threading.currentThread().name
        print time.ctime(), 'setting alarm in: ', t_name
        signal.alarm(1)
        print time.ctime(), 'Sleeping in: ', t_name
        time.sleep(5)
        print time.ctime(), 'Done with sleep in: ', t_name

    #start a thread that will not receive the signal
    alarm_thread = threading.Thread(target=use_alarm, name='alarm_thread')

    alarm_thread.start()
    time.sleep(0.1)

    #wait for the thread to see the signal (not going to happen!)
    print time.ctime(), 'Waiting for ', alarm_thread.name
    alarm_thread.join()

    print time.ctime(), 'Exiting normally'

if __name__ == '__main__':
    #test_bind_signal() #another terminal to os.kill(pid, signal.SIGTERM)

    #test_child_process_signal_parent()

    #test_signal_alarm()

    #test_signal_thread()

    test_alarm_only_received_by_main_thread()

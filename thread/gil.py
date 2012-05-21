#!/bin/bash python
#-*- coding='utf-8' -*-

def test_dead_loop():
    '''100%CPU'''
    while True:
        pass

def test_multi_cpu_dead_loop():
    import threading

    t = threading.Thread(target=test_dead_loop)
    t.start()

    
    t1 = threading.Thread(target=test_dead_loop)
    t1.start()
    
    t1.join()
    t2.join()


if __name__ == '__main__':
    #test_dead_loop()
    test_multi_cpu_dead_loop()

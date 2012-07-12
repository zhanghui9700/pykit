#!/bin/bash python
#-*-coding=utf-8-*-

import pika

class Sender(object):
    def __init__(self,queueName=None):
        self._conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self._conn.channel()
        self.queue = self.channel.queue_declare(queue=queueName)

    def send(self,msg=None):
        assert msg is not None
        self.channel.basic_publish(exchange='',
                                    routing_key = 'hello',
                                    body = msg)
        print 'send [%s] to queue'%msg

    def close(self):
        if self._conn:
            self._conn.close()

if __name__ == '__main__':
    sender = Sender('hello')
    import time
    index = 1
    while index < 100:
        sender.send(msg="hello world_%s"%index)
        index += 1
        time.sleep(2)
    sender.close()
    print 'it works...done!!!'

#!/bin/bash python
#-*-coding=utf-8-*-

import pika

class Receiver(object):
    def __init__(self,queueName=None):
        self._conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self._conn.channel()
        self.queue = self.channel.queue_declare(queue=queueName)
        self.queueName = queueName 

    def receive(self):
        def _callback(ch,method,properties,body):
            print 'ch',ch
            print 'method',method
            print 'properties',properties
            print '[x] receiverd body:%s'% (body,)
            
        self.channel.basic_consume(_callback, 
                                queue=self.queueName,
                                no_ack=True)
        print '[*] wiating for messages...To exit press CTRL+C'
        self.channel.start_consuming()

if __name__ == '__main__':
    receiver = Receiver('hello')
    receiver.receive()


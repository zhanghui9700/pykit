#!/bin/bash python
#-*- coding=utf-8 -*-

import os,threading
import datetime
import time

def echo_server():
    from twisted.internet import protocol,reactor
    
    class Echo(protocol.Protocol):
        '''
        单进程单线程
        '''
        def dataReceived(self,data):
            time.sleep(5)
            now = datetime.datetime.now()
            print 'date:',now
            print 'pid:',os.getpid(),'thread:',threading.current_thread()._Thread__ident
            self.transport.write('[%s]:%s'%(now,data))

    class EchoFactory(protocol.Factory):
        def buildProtocol(self,addr):
            print 'echo()'
            return Echo()

    reactor.listenTCP(1234,EchoFactory())
    reactor.run()

def web_server():
    from twisted.web import server,resource
    from twisted.internet import reactor

    class IndexResource(resource.Resource):
        isLeaf = True
        numberRequests = 0

        def render_GET(self,request):
            self.numberRequests += 1
            request.setHeader("content-type","text/plain")

            return "[pid:%s,tid:%s]i am request #%s\n" % (os.getpid(),threading.current_thread()._Thread__ident,str(self.numberRequests))
    
    reactor.listenTCP(1234,server.Site(IndexResource()))
    reactor.run()

def publish_subscribe():
    from twisted.internet import protocol,reactor
    from twisted.protocols import basic

    class PublishProtocol(basic.LineReceiver):
        def __init__(self,factory):
            print '__inin__'
            self.factory = factory

        def connectionMade(self):
            print 'connection maded'
            self.factory.clients.add(self)

        def lineReceived(self,line):
            for c in self.factory.clients:
                print self.transport.getHost(),':',line
                c.sendLine("[pid:{2},tid:{3}]<{0}>{1}".format(self.transport.getHost(),line,os.getpid(),threading.current_thread()._Thread__ident))

    class PublishFactory(protocol.Factory):
        def __init__(self):
            self.clients = set()

        def buildProtocol(self,addr):
            return PublishProtocol(self)

    reactor.listenTCP(1234,PublishFactory())
    reactor.run()

if __name__ == '__main__':
    #echo_server()
    #web_server()
    publish_subscribe()

#!/bin/bash python
#-*- coding = utf-8 -*-

import time

import tornado.ioloop
import tornado.web


request = tornado.web.RequestHandler

class MainHandler(request):
    def get(self):
        time.sleep(5)
        self.write('hello,world!')

class DateHandler(request):
    def get(self,year=2012,month=1):
        self.write('you request the date is:%s-%s'%(year,month))

application = tornado.web.Application(
    [
        (r'/',MainHandler),
        (r'/date/([\d]{4})/([\d]{1,2})',DateHandler),
    ]
)

if __name__ == '__main__':
    application.listen(9800)
    tornado.ioloop.IOLoop.instance().start()

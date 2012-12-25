#!/usr/bin/env python
#-*-coding=utf-8-*-

import sys
import os
import time
import select
import traceback
import win32serviceutil
import win32service
import win32event
#import win32traceutil
import servicemanager
import winerror

from threading import Thread, Event

from bottle import ServerAdapter, run as bottle_run
from action import app
from utility import network

__bottle_app__ = app
__host__ = '0.0.0.0'
__port__ = '9999'


def getTrace():
    """ retrieve and format an exception into a nice message
"""
    msg = traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1],
        sys.exc_info()[2])
    msg = ''.join(msg)
    msg = msg.split('\012')
    msg = ''.join(msg)
    msg += '\n'
    return msg


class WSGIRefHandleOneServer(ServerAdapter):
    def run(self, handler): # pragma: no cover
        import servicemanager
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        handler_class = WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            handler_class = QuietHandler
        srv = make_server(self.host, self.port, handler, handler_class=handler_class)
        servicemanager.LogInfoMsg("Bound to %s:%s" % (__host__ or '0.0.0.0', __port__))
        srv_wait = srv.fileno()
        while self.options['notifyEvent'].isSet():
            ready = select.select([srv_wait], [], [], 1)
            if srv_wait in ready[0]:
                srv.handle_request()
            continue

class BottleWsgiServer(Thread):

    def __init__(self, eventNotifyObj):
        Thread.__init__(self)
        self.notifyEvent = eventNotifyObj

    def run ( self ):
        bottle_run(__bottle_app__, host=__host__, port=__port__, server=WSGIRefHandleOneServer, reloader=False,
                    quiet=True, notifyEvent=self.notifyEvent)


class EayunVMToolsWindowsService(win32serviceutil.ServiceFramework):
    """ Windows NT Service class for running a bottle.py server """

    _svc_name_ = 'EayunVMToolsWindows'
    _svc_display_name_ = 'Eayun vm tools for windows'
    _svc_description_ = 'Eayun vm tools for windows'
    #_svc_deps = ['EventLog']

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        # Create an event which we will use to wait on.
        # The "service stop" request will set this event.
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
 
    def SvcStop(self):
        # Before we do anything, tell the SCM we are starting the stop process.
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # stop the process if necessary
        self.thread_event.clear()
        self.bottle_srv.join()

        # And set my event.
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False

    # SvcStop only gets triggered when the user explicitly stops (or restarts)
    # the service. To shut the service down cleanly when Windows is shutting
    # down, we also need to hook SvcShutdown.
    SvcShutdown = SvcStop

    def SvcDoRun(self):
        import servicemanager
        
        print 'begin to start'
        while self.is_alive:
            self.thread_event = Event()
            self.thread_event.set()
            try:
                self.bottle_srv = BottleWsgiServer(self.thread_event)
                self.bottle_srv.start()
            except Exception, info:
                errmsg = getTrace()
                servicemanager.LogErrorMsg(errmsg)
                self.SvcStop()

            rc = win32event.WaitForMultipleObjects((self.hWaitStop,), 0,
                win32event.INFINITE)
            if rc == win32event.WAIT_OBJECT_0:
                # user sent a stop service request
                self.SvcStop()
                break


if __name__=='__main__':
    print len(sys.argv), sys.argv
    if len(sys.argv) == 1:
        try:
            src_dll = os.path.abspath(servicemanager .__file__)
            servicemanager.PrepareToHostSingle(EayunVMToolsWindowsService)
            servicemanager.Initialize('EayunVMToolsWindowsService', src_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error, details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(EayunVMToolsWindowsService)

#!/usr/bin/env python
#-*-coding=utf-8-*-

#vim:tabstop=4 shiftwidth=4 softtabstop=4

import logging

A = "FIRST"
B = "FIRST.SECOND"
C = "FIRST.SECOND.THRID"

DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)8s [%(name)s] %(message)s"
DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


if __name__ == '__main__':
    root = logging.getLogger(A)
    log_format = logging.Formatter(fmt=DEFAULT_LOG_FORMAT,\
                                datefmt=DEFAULT_LOG_DATE_FORMAT)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    root.addHandler(logging.StreamHandler())
    
    file_handler = logging.FileHandler('/tmp/nova/nova-api.log')
    file_handler.setFormatter(log_format)
    root.addHandler(file_handler)

    root.setLevel(logging.DEBUG)
    
    log = logging.getLogger('hellopython')
    print log.__dict__
    log.info('hellopython:%s'%log.name)

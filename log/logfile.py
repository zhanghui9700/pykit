#!/usr/bin/env python
#-*-coding=utf-8-*-

import os
import sys
import logging
import platform

_loggers = {}

DEFAULT_LOG_FORMAT = '%(asctime)s %(levelname)8s [%(name)s] %(message)s'
DEFAULT_LOG_DATE_FORMAT = '[%Y-%m-%d %H:%M:%S]>'

def getLogger(name):
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name) 
    if platform.system().lower() == 'windows':
        return logger

    if not logger.handlers:
        log_format = logging.Formatter(fmt=DEFAULT_LOG_FORMAT, \
                                        datefmt=DEFAULT_LOG_DATE_FORMAT) 
        log_path = os.path.normpath(os.path.join(os.path.abspath(__file__),\
                            os.path.pardir, os.path.pardir,'%s.log'%name))
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(log_format)
        
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)

    _loggers[name] = logger
    return _loggers[name]
        

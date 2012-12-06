#!/usr/bin/env python
#-*-coding=utf-8-*-

import os
import logging

from logging.config import dictConfig

LOGGING = {
     "version": 1,
     "formatters": {
         "plain": {
             "format": "%(asctime)s %(message)s"
         },
         "verbose": {
             "format": "%(asctime)s %(levelname)s %(message)s",
             "datefmt": "%a, %d %b %Y %H:%M:%S",
         },
     },
     "handlers": {
          "console":{
             "level":"DEBUG",
             "class":"logging.StreamHandler",
             "formatter": "verbose",
         },
         'logfile': {
             'level': 'DEBUG',
             'class': 'logging.handlers.RotatingFileHandler',
             'formatter': 'verbose',
             'filename': os.path.join(os.getcwd(),'test.log'),
             'mode': 'a',
         },
     },
     "loggers": {
         "default": {
             "handlers": ["logfile", "console"],
             "level": "DEBUG",
             "propagate": False,
         },
         "deprecated": {
             "handlers": ["console"],
             "level": "DEBUG",
             "propagate": False,
         },
     }
 }


def do_test():
    dictConfig(LOGGING)
    logger = logging.getLogger()
    logger.exception(Exception('test'))

    logger2 = logging.getLogger("default")
    logger2.exception(Exception('test'))

if __name__ == '__main__':
    do_test()

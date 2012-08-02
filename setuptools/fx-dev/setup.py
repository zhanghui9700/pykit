#!/bin/bash python
#-*-coding=utf-8-*-

import os
from setuptools import setup

def readme():
    return open(os.path.join(os.path.dirname(__file__),"README")).read()

setup(
    name = "setup example 1",
    version = "0.1.0",
    author = "zhanghui",
    author_email = "demo@project.com",
    description = ("hello python!!!",),
    license = "BSD",
    keywords = "setuptools setup",
    url = "http://google.com/",
    packages = [],
    long_description = readme(),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)

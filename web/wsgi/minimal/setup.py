#!/usr/bin/env python
#-*-coding=utf-8-*-

import os
from setuptools import setup, find_packages

version = '1.0'

setup(name = 'minimal',
      version = version,
      description = "",
      long_description = """
        very, very minimal example of a WSGI application and middleware.
      """,
      classifiers = ["Programming Language :: Python",],
      keywords = 'wsgi paste',
      author = "pykit",
      author_email = "zhanghui9700@gmail.com",
      url = "",
      license = "BSD",
      include_package_data = True,
      packages = ['minimal',],
      zip_safe = False,
      install_requires = ["setuptools",],
      entry_points = """
      [paste.app_factory]
      main = minimal:main

      [paste.filter_factory]
      main = minimal:middleware
      """,
      )


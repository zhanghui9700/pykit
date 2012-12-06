from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='minimal',
      version=version,
      description="",
      long_description="""
         Very, very minimal example of a WSGI application and middleware.
      """,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Josh Johnson',
      author_email='none of your beeswax@somehost.com',
      url='http://lionfacelemonface.wordpress.com',
      license='BSD',
      include_package_data=True,
      packages=['minimal',],
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      [paste.app_factory] 
      main = minimal:main
      """,
      )

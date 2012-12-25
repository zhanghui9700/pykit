#!/usr/bin/env python
#-*-coding=utf-8-*-

from distutils.core import setup
import py2exe

includes = ["encodings", "encodings.*"]  
 
options = {"py2exe":
            {"compressed": 1,
             "optimize": 2,
             "ascii": 1,
             "includes":includes,
             "bundle_files": 1 
            }}
setup(
    options=options,
    zipfile=None,
    #console=[{"windows": "EAYUN_VM_TOOLS.py",}],  
    #windows=[{"script": "EAYUN_VM_TOOLS.py",}],  
    service=["EayunVMToolsWindows"],
    version = "v1.0.0.1.20121129174019",   
    description = "eayun vm tools!", 
    name = "eayun_vm_tools", 
)

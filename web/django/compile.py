#!/usr/bin/env python
#-*-coding=utf-8-*-

import os
import sys
import compileall


def do_compile(dir_path):
    compileall.compile_dir(dir_path)

def rm_pyfile(dir_path):
    pass 

def do_rename_managepy(dir_path,old_name,new_name):
    f = os.path.join(dir_path,old_name)
    if not os.path.isfile(f):
        raise Exception("%s not existed!can't rename."%f)

    os.renames(f,os.path.join(dir_path,new_name))

def do_rm_pyfile(dir_path):
    os.system('find %s -type f -name "*.py"|xargs rm -rf'%dir_path)

if __name__ == "__main__":
    TOOL_DIR = os.path.dirname(os.path.realpath(__file__))
    PROJECT_DIR = os.path.join(TOOL_DIR,"..","eayuncenter")
    
    if not os.path.isdir(PROJECT_DIR):
        raise Exception('PROJECT_DIR:[%s] not existed!')

    do_rename_managepy(PROJECT_DIR,"manage.py","manage.sh")
    do_compile(PROJECT_DIR) 
    do_rm_pyfile(PROJECT_DIR)
    do_rename_managepy(PROJECT_DIR,"manage.sh","manage.py")

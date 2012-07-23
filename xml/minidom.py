#!/bin/bash python
#-*-coding=utf-8-*-

from xml.dom import minidom

LIBVIRT_PATH = "/home/zhanghui/github/pykit/xml/libvirt.xml"
CHANGED_LIBVIRT_PATH = "/home/zhanghui/github/pykit/xml/libvirt_new.xml"

if __name__ == "__main__":
    dom = minidom.parse(LIBVIRT_PATH)
    root = dom.documentElement
    print root.nodeName
    print root.toxml()
    print root.childNodes

    vcpu = dom.getElementsByTagName('vcpu')[0].childNodes[0]
    print vcpu.data
    vcpu.data = 4

    f = open(CHANGED_LIBVIRT_PATH,'w')
    f.write(root.toxml())
    f.close()

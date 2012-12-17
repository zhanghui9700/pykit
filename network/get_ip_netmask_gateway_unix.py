#!/usr/bin/env python
#-*-coding=utf-8-*-

import os
import socket
import fcntl
import struct
 
SIOCGIFNETMASK = 0x891b
 
def get_network_mask(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    netmask = fcntl.ioctl(s, SIOCGIFNETMASK, struct.pack('256s', ifname))[20:24]
    return socket.inet_ntoa(netmask)
 
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
 
def get_gateway(ifname):
    cmd = "ip route list dev "+ ifname + " | awk ' /^default/ {print $3}'"
    fin,fout = os.popen4(cmd)
    result = fout.read()
    return result


#Read more: http://thiagodefreitas.com/blog#ixzz2FHh1ZFIh 
#Under Creative Commons License: Attribution

if __name__ == '__main__':
    print get_network_mask('eth0') 
    print get_ip_address('eth0')
    print get_gateway('eth0')

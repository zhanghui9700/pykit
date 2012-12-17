#!/usr/bin/env python
#-*-coding=utf-8-*-

#Snippet for getting the default gateway on Linux
#No dependencies beyond Python stdlib

import platform
import socket, struct
 
def get_default_gateway_linux():
    """Read the default gateway directly from /proc."""
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
 
            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

def get_default_gateway_windows():
   import wmi

   wmi_obj = wmi.WMI()
   wmi_sql = "select IPAddress,DefaultIPGateway from Win32_NetworkAdapterConfiguration where IPEnabled=TRUE"
   wmi_out = wmi_obj.query( wmi_sql )

   #for dev in wmi_out:
   #    print "IPv4Address:", dev.IPAddress[0], "DefaultIPGateway:", dev.DefaultIPGateway[0]

   return wmi_out[0].DefaultIPGateway[0]

if __name__ == '__main__':
    if platform.system().lower() == 'windows':
        print get_default_gateway_windows()
    else:
        print get_default_gateway_linux()

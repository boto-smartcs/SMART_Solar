import socket
import os
import netifaces

def getNetworkIp():
    gw = os.popen("ip -4 route show default").read().split()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((gw[2], 0))
    ipaddr = s.getsockname()[0]
    gateway = gw[2]
    # host = socket.gethostname()
    subnetmask = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['netmask']
    return ipaddr, gateway, subnetmask
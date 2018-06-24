# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 06:54:31 2017

@author: mtkes
"""

import ifaddr

adapters = ifaddr.get_adapters()

for adapter in adapters:
    print("IPs of network adapter " + adapter.nice_name)
    for ip in adapter.ips:
        print("   %s/%s" % (ip.ip, ip.network_prefix))
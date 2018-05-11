from swsscommon import swsscommon
import os
import re
import time
import json

def test_InvalidNexthop(dvs):

    dvs.copy_file("/etc/quagga/", "bgp/files/bgpd.conf")
    dvs.runcmd("supervisorctl start bgpd")
    dvs.runcmd("ip addr add fc00::1/126 dev Ethernet0")
    dvs.runcmd("ifconfig Ethernet0 up")

    dvs.servers[0].runcmd("ip addr add fc00::2/126 dev eth0")
    dvs.servers[0].runcmd("ifconfig eth0 up")

    time.sleep(5)

    print dvs.runcmd("supervisorctl status")

    p = dvs.servers[0].runcmd_async("exabgp -d bgp/files/invalid_nexthop.conf")

    time.sleep(10)

    output = dvs.runcmd(["vtysh", "-c", "show ipv6 bgp"])

    p.terminate()
    p = p.wait()

    print output

    assert "3333::/64" in output

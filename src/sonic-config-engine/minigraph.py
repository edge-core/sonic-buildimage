#!/usr/bin/env python
import calendar
import os
import sys
import socket
import struct
import json
import copy
import ipaddr as ipaddress
from collections import defaultdict

from lxml import etree as ET
from lxml.etree import QName

from portconfig import get_port_config

"""minigraph.py
version_added: "1.9"
author: Guohan Lu (gulv@microsoft.com)
short_description: Parse minigraph xml file and device description xml file
"""

ns = "Microsoft.Search.Autopilot.Evolution"
ns1 = "http://schemas.datacontract.org/2004/07/Microsoft.Search.Autopilot.Evolution"
ns2 = "Microsoft.Search.Autopilot.NetMux"
ns3 = "http://www.w3.org/2001/XMLSchema-instance"
KEY_SEPARATOR = '|'

class minigraph_encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (
            ipaddress.IPv4Network, ipaddress.IPv6Network,
            ipaddress.IPv4Address, ipaddress.IPv6Address
            )):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def parse_device(device):
    lo_prefix = None
    mgmt_prefix = None
    d_type = None   # don't shadow type()
    hwsku = None
    name = None
    if str(QName(ns3, "type")) in device.attrib:
        d_type = device.attrib[str(QName(ns3, "type"))]

    for node in device:
        if node.tag == str(QName(ns, "Address")):
            lo_prefix = node.find(str(QName(ns2, "IPPrefix"))).text
        elif node.tag == str(QName(ns, "ManagementAddress")):
            mgmt_prefix = node.find(str(QName(ns2, "IPPrefix"))).text
        elif node.tag == str(QName(ns, "Hostname")):
            name = node.text
        elif node.tag == str(QName(ns, "HwSku")):
            hwsku = node.text
    return (lo_prefix, mgmt_prefix, name, hwsku, d_type)

def parse_png(png, hname):
    neighbors = {}
    devices = {}
    console_dev = ''
    console_port = ''
    mgmt_dev = ''
    mgmt_port = ''
    for child in png:
        if child.tag == str(QName(ns, "DeviceInterfaceLinks")):
            for link in child.findall(str(QName(ns, "DeviceLinkBase"))):
                linktype = link.find(str(QName(ns, "ElementType"))).text
                if linktype != "DeviceInterfaceLink" and linktype != "UnderlayInterfaceLink":
                    continue

                enddevice = link.find(str(QName(ns, "EndDevice"))).text
                endport = link.find(str(QName(ns, "EndPort"))).text
                startdevice = link.find(str(QName(ns, "StartDevice"))).text
                startport = link.find(str(QName(ns, "StartPort"))).text

                if enddevice == hname:
                    if port_alias_map.has_key(endport):
                        endport = port_alias_map[endport]
                    neighbors[endport] = {'name': startdevice, 'port': startport}
                else:
                    if port_alias_map.has_key(startport):
                        startport = port_alias_map[startport]
                    neighbors[startport] = {'name': enddevice, 'port': endport}

        if child.tag == str(QName(ns, "Devices")):
            for device in child.findall(str(QName(ns, "Device"))):
                (lo_prefix, mgmt_prefix, name, hwsku, d_type) = parse_device(device)
                device_data = {'lo_addr': lo_prefix, 'type': d_type, 'mgmt_addr': mgmt_prefix, 'hwsku': hwsku }
                devices[name] = device_data

        if child.tag == str(QName(ns, "DeviceInterfaceLinks")):
            for if_link in child.findall(str(QName(ns, 'DeviceLinkBase'))):
                if str(QName(ns3, "type")) in if_link.attrib:
                    link_type = if_link.attrib[str(QName(ns3, "type"))]
                    if link_type == 'DeviceSerialLink':
                        for node in if_link:
                            if node.tag == str(QName(ns, "EndPort")):
                                console_port = node.text.split()[-1]
                            elif node.tag == str(QName(ns, "EndDevice")):
                                console_dev = node.text
                    elif link_type == 'DeviceMgmtLink':
                        for node in if_link:
                            if node.tag == str(QName(ns, "EndPort")):
                                mgmt_port = node.text.split()[-1]
                            elif node.tag == str(QName(ns, "EndDevice")):
                                mgmt_dev = node.text

    return (neighbors, devices, console_dev, console_port, mgmt_dev, mgmt_port)


def parse_dpg(dpg, hname):
    for child in dpg:
        hostname = child.find(str(QName(ns, "Hostname")))
        if hostname.text != hname:
            continue

        ipintfs = child.find(str(QName(ns, "IPInterfaces")))
        intfs = {}
        for ipintf in ipintfs.findall(str(QName(ns, "IPInterface"))):
            intfalias = ipintf.find(str(QName(ns, "AttachTo"))).text
            intfname = port_alias_map.get(intfalias, intfalias)
            ipprefix = ipintf.find(str(QName(ns, "Prefix"))).text
            intfs[(intfname, ipprefix)] = {}

        lointfs = child.find(str(QName(ns, "LoopbackIPInterfaces")))
        lo_intfs = {}
        for lointf in lointfs.findall(str(QName(ns1, "LoopbackIPInterface"))):
            intfname = lointf.find(str(QName(ns, "AttachTo"))).text
            ipprefix = lointf.find(str(QName(ns1, "PrefixStr"))).text
            lo_intfs[(intfname, ipprefix)] = {}

        mgmtintfs = child.find(str(QName(ns, "ManagementIPInterfaces")))
        mgmt_intf = {}
        for mgmtintf in mgmtintfs.findall(str(QName(ns1, "ManagementIPInterface"))):
            intfname = mgmtintf.find(str(QName(ns, "AttachTo"))).text
            ipprefix = mgmtintf.find(str(QName(ns1, "PrefixStr"))).text
            mgmtipn = ipaddress.IPNetwork(ipprefix)
            gwaddr = ipaddress.IPAddress(int(mgmtipn.network) + 1)
            mgmt_intf[(intfname, ipprefix)] = {'gwaddr': gwaddr}

        pcintfs = child.find(str(QName(ns, "PortChannelInterfaces")))
        pc_intfs = []
        pcs = {}
        for pcintf in pcintfs.findall(str(QName(ns, "PortChannel"))):
            pcintfname = pcintf.find(str(QName(ns, "Name"))).text
            pcintfmbr = pcintf.find(str(QName(ns, "AttachTo"))).text
            pcmbr_list = pcintfmbr.split(';')
            for i, member in enumerate(pcmbr_list):
                pcmbr_list[i] = port_alias_map.get(member, member)
            if pcintf.find(str(QName(ns, "Fallback"))) != None:
                pcs[pcintfname] = {'members': pcmbr_list, 'fallback': pcintf.find(str(QName(ns, "Fallback"))).text}
            else:
                pcs[pcintfname] = {'members': pcmbr_list}

        vlanintfs = child.find(str(QName(ns, "VlanInterfaces")))
        vlan_intfs = []
        vlans = {}
        vlan_members = {}
        for vintf in vlanintfs.findall(str(QName(ns, "VlanInterface"))):
            vintfname = vintf.find(str(QName(ns, "Name"))).text
            vlanid = vintf.find(str(QName(ns, "VlanID"))).text
            vintfmbr = vintf.find(str(QName(ns, "AttachTo"))).text
            vmbr_list = vintfmbr.split(';')
            for i, member in enumerate(vmbr_list):
                vmbr_list[i] = port_alias_map.get(member, member)
                sonic_vlan_member_name = "Vlan%s%s%s" % (vlanid, KEY_SEPARATOR, vmbr_list[i])
                vlan_members[sonic_vlan_member_name] = {'tagging_mode': 'untagged'}

            vlan_attributes = {'vlanid': vlanid}

            # If this VLAN requires a DHCP relay agent, it will contain a <DhcpRelays> element
            # containing a list of DHCP server IPs
            if vintf.find(str(QName(ns, "DhcpRelays"))) is not None:
                vintfdhcpservers = vintf.find(str(QName(ns, "DhcpRelays"))).text
                vdhcpserver_list = vintfdhcpservers.split(';')
                vlan_attributes['dhcp_servers'] = vdhcpserver_list

            sonic_vlan_name = "Vlan%s" % vlanid
            vlans[sonic_vlan_name] = vlan_attributes

        aclintfs = child.find(str(QName(ns, "AclInterfaces")))
        acls = {}
        for aclintf in aclintfs.findall(str(QName(ns, "AclInterface"))):
            aclname = aclintf.find(str(QName(ns, "InAcl"))).text.upper().replace(" ", "_").replace("-", "_")
            aclattach = aclintf.find(str(QName(ns, "AttachTo"))).text.split(';')
            acl_intfs = []
            is_mirror = False
            for member in aclattach:
                member = member.strip()
                if pcs.has_key(member):
                    acl_intfs.extend(pcs[member]['members'])  # For ACL attaching to port channels, we break them into port channel members
                elif vlans.has_key(member):
                    print >> sys.stderr, "Warning: ACL " + aclname + " is attached to a Vlan interface, which is currently not supported"
                elif port_alias_map.has_key(member):
                    acl_intfs.append(port_alias_map[member])
                elif member.lower() == 'erspan':
                    is_mirror = True;
                    # Erspan session will be attached to all front panel ports
                    acl_intfs = port_alias_map.values()
                    break;
            if acl_intfs:
                acls[aclname] = { 'policy_desc': aclname, 'ports': acl_intfs, 'type': 'MIRROR' if is_mirror else 'L3'}
        return intfs, lo_intfs, mgmt_intf, vlans, vlan_members, pcs, acls
    return None, None, None, None, None, None, None


def parse_cpg(cpg, hname):
    bgp_sessions = {}
    myasn = None
    bgp_peers_with_range = {}
    for child in cpg:
        tag = child.tag
        if tag == str(QName(ns, "PeeringSessions")):
            for session in child.findall(str(QName(ns, "BGPSession"))):
                start_router = session.find(str(QName(ns, "StartRouter"))).text
                start_peer = session.find(str(QName(ns, "StartPeer"))).text
                end_router = session.find(str(QName(ns, "EndRouter"))).text
                end_peer = session.find(str(QName(ns, "EndPeer"))).text
                rrclient = 1 if session.find(str(QName(ns, "RRClient"))) is not None else 0
                if session.find(str(QName(ns, "HoldTime"))) is not None:
                    holdtime = session.find(str(QName(ns, "HoldTime"))).text
                else:
                    holdtime = 180
                if session.find(str(QName(ns, "KeepAliveTime"))) is not None:
                    keepalive = session.find(str(QName(ns, "KeepAliveTime"))).text
                else:
                    keepalive = 60
                nhopself = 1 if session.find(str(QName(ns, "NextHopSelf"))) is not None else 0
                if end_router == hname:
                    bgp_sessions[start_peer] = {
                        'name': start_router,
                        'local_addr': end_peer,
                        'rrclient': rrclient,
                        'holdtime': holdtime,
                        'keepalive': keepalive,
                        'nhopself': nhopself
                    }
                else:
                    bgp_sessions[end_peer] = {
                        'name': end_router,
                        'local_addr': start_peer,
                        'rrclient': rrclient,
                        'holdtime': holdtime,
                        'keepalive': keepalive,
                        'nhopself': nhopself
                    }
        elif child.tag == str(QName(ns, "Routers")):
            for router in child.findall(str(QName(ns1, "BGPRouterDeclaration"))):
                asn = router.find(str(QName(ns1, "ASN"))).text
                hostname = router.find(str(QName(ns1, "Hostname"))).text
                if hostname == hname:
                    myasn = asn
                    peers = router.find(str(QName(ns1, "Peers")))
                    for bgpPeer in peers.findall(str(QName(ns, "BGPPeer"))):
                        addr = bgpPeer.find(str(QName(ns, "Address"))).text
                        if bgpPeer.find(str(QName(ns1, "PeersRange"))) is not None:
                            name = bgpPeer.find(str(QName(ns1, "Name"))).text
                            ip_range = bgpPeer.find(str(QName(ns1, "PeersRange"))).text
                            ip_range_group = ip_range.split(';') if ip_range and ip_range != "" else []
                            bgp_peers_with_range[name] = {
                                'name': name,
                                'ip_range': ip_range_group
                            }
                else:
                    for peer in bgp_sessions:
                        bgp_session = bgp_sessions[peer]
                        if hostname == bgp_session['name']:
                            bgp_session['asn'] = asn
    bgp_sessions = { key: bgp_sessions[key] for key in bgp_sessions if bgp_sessions[key].has_key('asn') and int(bgp_sessions[key]['asn']) != 0 }
    return bgp_sessions, myasn, bgp_peers_with_range


def parse_meta(meta, hname):
    syslog_servers = []
    dhcp_servers = []
    ntp_servers = []
    mgmt_routes = []
    erspan_dst = []
    deployment_id = None
    device_metas = meta.find(str(QName(ns, "Devices")))
    for device in device_metas.findall(str(QName(ns1, "DeviceMetadata"))):
        if device.find(str(QName(ns1, "Name"))).text == hname:
            properties = device.find(str(QName(ns1, "Properties")))
            for device_property in properties.findall(str(QName(ns1, "DeviceProperty"))):
                name = device_property.find(str(QName(ns1, "Name"))).text
                value = device_property.find(str(QName(ns1, "Value"))).text
                value_group = value.split(';') if value and value != "" else []
                if name == "DhcpResources":
                    dhcp_servers = value_group
                elif name == "NtpResources":
                    ntp_servers = value_group
                elif name == "SyslogResources":
                    syslog_servers = value_group
                elif name == "ForcedMgmtRoutes":
                    mgmt_routes = value_group
                elif name == "ErspanDestinationIpv4":
                    erspan_dst = value_group
                elif name == "DeploymentId":
                    deployment_id = value
    return syslog_servers, dhcp_servers, ntp_servers, mgmt_routes, erspan_dst, deployment_id

def parse_deviceinfo(meta, hwsku):
    port_speeds = {}
    port_descriptions = {}
    for device_info in meta.findall(str(QName(ns, "DeviceInfo"))):
        dev_sku = device_info.find(str(QName(ns, "HwSku"))).text
        if dev_sku == hwsku:
            interfaces = device_info.find(str(QName(ns, "EthernetInterfaces")))
            for interface in interfaces.findall(str(QName(ns1, "EthernetInterface"))):
                alias = interface.find(str(QName(ns, "InterfaceName"))).text
                speed = interface.find(str(QName(ns, "Speed"))).text
                desc  = interface.find(str(QName(ns, "Description")))
                if desc != None:
                    port_descriptions[port_alias_map.get(alias, alias)] = desc.text
                port_speeds[port_alias_map.get(alias, alias)] = speed
    return port_speeds, port_descriptions

def parse_xml(filename, platform=None, port_config_file=None):
    root = ET.parse(filename).getroot()
    mini_graph_path = filename

    u_neighbors = None
    u_devices = None
    hwsku = None
    bgp_sessions = None
    bgp_asn = None
    intfs = None
    vlan_intfs = None
    pc_intfs = None
    vlans = None
    vlan_members = None
    pcs = None
    mgmt_intf = None
    lo_intf = None
    neighbors = None
    devices = None
    hostname = None
    port_speeds = {}
    port_descriptions = {}
    syslog_servers = []
    dhcp_servers = []
    ntp_servers = []
    mgmt_routes = []
    erspan_dst = []
    bgp_peers_with_range = None
    deployment_id = None

    hwsku_qn = QName(ns, "HwSku")
    hostname_qn = QName(ns, "Hostname")
    for child in root:
        if child.tag == str(hwsku_qn):
            hwsku = child.text
        if child.tag == str(hostname_qn):
            hostname = child.text

    (ports, alias_map) = get_port_config(hwsku, platform, port_config_file)
    port_alias_map.update(alias_map)
    for child in root:
        if child.tag == str(QName(ns, "DpgDec")):
            (intfs, lo_intfs, mgmt_intf, vlans, vlan_members, pcs, acls) = parse_dpg(child, hostname)
        elif child.tag == str(QName(ns, "CpgDec")):
            (bgp_sessions, bgp_asn, bgp_peers_with_range) = parse_cpg(child, hostname)
        elif child.tag == str(QName(ns, "PngDec")):
            (neighbors, devices, console_dev, console_port, mgmt_dev, mgmt_port) = parse_png(child, hostname)
        elif child.tag == str(QName(ns, "UngDec")):
            (u_neighbors, u_devices, _, _, _, _) = parse_png(child, hostname)
        elif child.tag == str(QName(ns, "MetadataDeclaration")):
            (syslog_servers, dhcp_servers, ntp_servers, mgmt_routes, erspan_dst, deployment_id) = parse_meta(child, hostname)
        elif child.tag == str(QName(ns, "DeviceInfos")):
            (port_speeds, port_descriptions) = parse_deviceinfo(child, hwsku)

    results = {}
    results['DEVICE_METADATA'] = {'localhost': {
        'bgp_asn': bgp_asn,
        'deployment_id': deployment_id,
        'hostname': hostname,
        'hwsku': hwsku,
        'type': devices[hostname]['type']
        }}
    results['BGP_NEIGHBOR'] = bgp_sessions
    results['BGP_PEER_RANGE'] = bgp_peers_with_range
    if mgmt_routes:
        # TODO: differentiate v4 and v6
        mgmt_intf.itervalues().next()['forced_mgmt_routes'] = mgmt_routes
    results['MGMT_INTERFACE'] = mgmt_intf
    results['LOOPBACK_INTERFACE'] = lo_intfs

    phyport_intfs = {}
    vlan_intfs = {}
    pc_intfs = {}
    for intf in intfs:
        if intf[0][0:4] == 'Vlan':
            vlan_intfs[intf] = {}
        elif intf[0][0:11] == 'PortChannel':
            pc_intfs[intf] = {}
        else:
            phyport_intfs[intf] = {}

    results['INTERFACE'] = phyport_intfs
    results['VLAN_INTERFACE'] = vlan_intfs
    results['PORTCHANNEL_INTERFACE'] = pc_intfs

    for port_name in port_speeds:
        ports.setdefault(port_name, {})['speed'] = port_speeds[port_name]
    for port_name in port_descriptions:
        ports.setdefault(port_name, {})['description'] = port_descriptions[port_name]

    results['PORT'] = ports
    results['PORTCHANNEL'] = pcs
    results['VLAN'] = vlans
    results['VLAN_MEMBER'] = vlan_members

    results['DEVICE_NEIGHBOR'] = neighbors
    results['DEVICE_NEIGHBOR_METADATA'] = { key:devices[key] for key in devices if key != hostname }
    results['SYSLOG_SERVER'] = dict((item, {}) for item in syslog_servers)
    results['DHCP_SERVER'] = dict((item, {}) for item in dhcp_servers)
    results['NTP_SERVER'] = dict((item, {}) for item in ntp_servers)

    results['ACL_TABLE'] = acls
    mirror_sessions = {}
    if erspan_dst:
        lo_addr = '0.0.0.0'
        for lo in lo_intfs:
            lo_network = ipaddress.IPNetwork(lo[1])
            if lo_network.version == 4:
                lo_addr = str(lo_network.ip)
                break
        count = 0
        for dst in erspan_dst:
            mirror_sessions['everflow{}'.format(count)] = {"dst_ip": dst, "src_ip": lo_addr}
            count += 1
        results['MIRROR_SESSION'] = mirror_sessions

    return results


def parse_device_desc_xml(filename):
    root = ET.parse(filename).getroot()
    (lo_prefix, mgmt_prefix, hostname, hwsku, d_type) = parse_device(root)

    results = {}
    results['DEVICE_METADATA'] = {'localhost': {
        'hostname': hostname,
        'hwsku': hwsku,
        }}

    results['LOOPBACK_INTERFACE'] = {('lo', lo_prefix): {}}

    mgmt_intf = {}
    mgmtipn = ipaddress.IPNetwork(mgmt_prefix)
    gwaddr = ipaddress.IPAddress(int(mgmtipn.network) + 1)
    results['MGMT_INTERFACE'] = {('eth0', mgmt_prefix): {'gwaddr': gwaddr}}

    return results


port_alias_map = {}


def print_parse_xml(filename):
    results = parse_xml(filename)
    print(json.dumps(results, indent=3, cls=minigraph_encoder))

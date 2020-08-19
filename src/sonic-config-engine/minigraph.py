#!/usr/bin/env python
from __future__ import print_function
import calendar
import math
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
from sonic_py_common.multi_asic import get_asic_id_from_name
from sonic_py_common.interface import backplane_prefix

"""minigraph.py
version_added: "1.9"
author: Guohan Lu (gulv@microsoft.com)
short_description: Parse minigraph xml file and device description xml file
"""

ns = "Microsoft.Search.Autopilot.Evolution"
ns1 = "http://schemas.datacontract.org/2004/07/Microsoft.Search.Autopilot.Evolution"
ns2 = "Microsoft.Search.Autopilot.NetMux"
ns3 = "http://www.w3.org/2001/XMLSchema-instance"

# Device types
spine_chassis_frontend_role = 'SpineChassisFrontendRouter'
chassis_backend_role = 'ChassisBackendRouter'

backend_device_types = ['BackEndToRRouter', 'BackEndLeafRouter']
VLAN_SUB_INTERFACE_SEPARATOR = '.'
VLAN_SUB_INTERFACE_VLAN_ID = '10'

FRONTEND_ASIC_SUB_ROLE = 'FrontEnd'
BACKEND_ASIC_SUB_ROLE = 'BackEnd'

# Default Virtual Network Index (VNI) 
vni_default = 8000

###############################################################################
#
# Minigraph parsing functions
#
###############################################################################

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
    deployment_id = None
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
        elif node.tag == str(QName(ns, "DeploymentId")):
            deployment_id = node.text
    return (lo_prefix, mgmt_prefix, name, hwsku, d_type, deployment_id)

def parse_png(png, hname):
    neighbors = {}
    devices = {}
    console_dev = ''
    console_port = ''
    mgmt_dev = ''
    mgmt_port = ''
    port_speeds = {}
    console_ports = {}
    for child in png:
        if child.tag == str(QName(ns, "DeviceInterfaceLinks")):
            for link in child.findall(str(QName(ns, "DeviceLinkBase"))):
                linktype = link.find(str(QName(ns, "ElementType"))).text
                if linktype == "DeviceSerialLink":
                    enddevice = link.find(str(QName(ns, "EndDevice"))).text
                    endport = link.find(str(QName(ns, "EndPort"))).text
                    startdevice = link.find(str(QName(ns, "StartDevice"))).text
                    startport = link.find(str(QName(ns, "StartPort"))).text
                    baudrate = link.find(str(QName(ns, "Bandwidth"))).text
                    flowcontrol = 1 if link.find(str(QName(ns, "FlowControl"))) is not None and link.find(str(QName(ns, "FlowControl"))).text == 'true' else 0
                    if enddevice.lower() == hname.lower():
                        console_ports[endport] = {
                            'remote_device': startdevice,
                            'baud_rate': baudrate,
                            'flow_control': flowcontrol
                            }
                    else:
                        console_ports[startport] = {
                            'remote_device': enddevice,
                            'baud_rate': baudrate,
                            'flow_control': flowcontrol
                            }
                    continue

                if linktype != "DeviceInterfaceLink" and linktype != "UnderlayInterfaceLink":
                    continue

                enddevice = link.find(str(QName(ns, "EndDevice"))).text
                endport = link.find(str(QName(ns, "EndPort"))).text
                startdevice = link.find(str(QName(ns, "StartDevice"))).text
                startport = link.find(str(QName(ns, "StartPort"))).text
                bandwidth_node = link.find(str(QName(ns, "Bandwidth")))
                bandwidth = bandwidth_node.text if bandwidth_node is not None else None
                if enddevice.lower() == hname.lower():
                    if endport in port_alias_map:
                        endport = port_alias_map[endport]
                    neighbors[endport] = {'name': startdevice, 'port': startport}
                    if bandwidth:
                        port_speeds[endport] = bandwidth
                elif startdevice.lower() == hname.lower():
                    if startport in port_alias_map:
                        startport = port_alias_map[startport]
                    neighbors[startport] = {'name': enddevice, 'port': endport}
                    if bandwidth:
                        port_speeds[startport] = bandwidth

        if child.tag == str(QName(ns, "Devices")):
            for device in child.findall(str(QName(ns, "Device"))):
                (lo_prefix, mgmt_prefix, name, hwsku, d_type, deployment_id) = parse_device(device)
                device_data = {'lo_addr': lo_prefix, 'type': d_type, 'mgmt_addr': mgmt_prefix, 'hwsku': hwsku }
                if deployment_id:
                    device_data['deployment_id'] = deployment_id
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

    return (neighbors, devices, console_dev, console_port, mgmt_dev, mgmt_port, port_speeds, console_ports)

def parse_asic_external_link(link, asic_name, hostname):
    neighbors = {}
    port_speeds = {}
    enddevice = link.find(str(QName(ns, "EndDevice"))).text
    endport = link.find(str(QName(ns, "EndPort"))).text
    startdevice = link.find(str(QName(ns, "StartDevice"))).text
    startport = link.find(str(QName(ns, "StartPort"))).text
    bandwidth_node = link.find(str(QName(ns, "Bandwidth")))
    bandwidth = bandwidth_node.text if bandwidth_node is not None else None
    # if chassis internal is false, the interface name will be
    # interface alias which should be converted to asic port name
    if (enddevice.lower() == hostname.lower()):
        if ((endport in port_alias_asic_map) and
                (asic_name.lower() in port_alias_asic_map[endport].lower())):
            endport = port_alias_asic_map[endport]
            neighbors[port_alias_map[endport]] = {'name': startdevice, 'port': startport}
            if bandwidth:
                port_speeds[port_alias_map[endport]] = bandwidth
    elif (startdevice.lower() == hostname.lower()):
        if ((startport in port_alias_asic_map) and
                (asic_name.lower() in port_alias_asic_map[startport].lower())):
            startport = port_alias_asic_map[startport]
            neighbors[port_alias_map[startport]] = {'name': enddevice, 'port': endport}
            if bandwidth:
                port_speeds[port_alias_map[startport]] = bandwidth

    return neighbors, port_speeds

def parse_asic_internal_link(link, asic_name, hostname):
    neighbors = {}
    port_speeds = {}
    enddevice = link.find(str(QName(ns, "EndDevice"))).text
    endport = link.find(str(QName(ns, "EndPort"))).text
    startdevice = link.find(str(QName(ns, "StartDevice"))).text
    startport = link.find(str(QName(ns, "StartPort"))).text
    bandwidth_node = link.find(str(QName(ns, "Bandwidth")))
    bandwidth = bandwidth_node.text if bandwidth_node is not None else None
    if ((enddevice.lower() == asic_name.lower()) and
            (startdevice.lower() != hostname.lower())):
        if endport in port_alias_map:
            endport = port_alias_map[endport]
            neighbors[endport] = {'name': startdevice, 'port': startport}
            if bandwidth:
                port_speeds[endport] = bandwidth
    elif ((startdevice.lower() == asic_name.lower()) and
            (enddevice.lower() != hostname.lower())):
        if startport in port_alias_map:
            startport = port_alias_map[startport]
            neighbors[startport] = {'name': enddevice, 'port': endport}
            if bandwidth:
                port_speeds[startport] = bandwidth

    return neighbors, port_speeds

def parse_asic_png(png, asic_name, hostname):
    neighbors = {}
    devices = {}
    port_speeds = {}
    for child in png:
        if child.tag == str(QName(ns, "DeviceInterfaceLinks")):
            for link in child.findall(str(QName(ns, "DeviceLinkBase"))):
                # Chassis internal node is used in multi-asic device or chassis minigraph
                # where the minigraph will contain the internal asic connectivity and
                # external neighbor information. The ChassisInternal node will be used to
                # determine if the link is internal to the device or chassis.
                chassis_internal_node = link.find(str(QName(ns, "ChassisInternal")))
                chassis_internal = chassis_internal_node.text if chassis_internal_node is not None else "false"

                # If the link is an external link include the external neighbor
                # information in ASIC ports table
                if chassis_internal.lower() == "false":
                    ext_neighbors, ext_port_speeds = parse_asic_external_link(link, asic_name, hostname)
                    neighbors.update(ext_neighbors)
                    port_speeds.update(ext_port_speeds)
                else:
                    int_neighbors, int_port_speeds = parse_asic_internal_link(link, asic_name, hostname)
                    neighbors.update(int_neighbors)
                    port_speeds.update(int_port_speeds)

        if child.tag == str(QName(ns, "Devices")):
            for device in child.findall(str(QName(ns, "Device"))):
                (lo_prefix, mgmt_prefix, name, hwsku, d_type, deployment_id) = parse_device(device)
                device_data = {'lo_addr': lo_prefix, 'type': d_type, 'mgmt_addr': mgmt_prefix, 'hwsku': hwsku }
                if deployment_id:
                    device_data['deployment_id'] = deployment_id
                devices[name] = device_data
    return (neighbors, devices, port_speeds)

def parse_loopback_intf(child):
    lointfs = child.find(str(QName(ns, "LoopbackIPInterfaces")))
    lo_intfs = {}
    for lointf in lointfs.findall(str(QName(ns1, "LoopbackIPInterface"))):
        intfname = lointf.find(str(QName(ns, "AttachTo"))).text
        ipprefix = lointf.find(str(QName(ns1, "PrefixStr"))).text
        lo_intfs[(intfname, ipprefix)] = {}
    return lo_intfs

def parse_dpg(dpg, hname):
    aclintfs = None
    mgmtintfs = None
    for child in dpg:
        """ 
            In Multi-NPU platforms the acl intfs are defined only for the host not for individual asic.
            There is just one aclintf node in the minigraph
            Get the aclintfs node first.
        """
        if aclintfs is None and child.find(str(QName(ns, "AclInterfaces"))) is not None:
            aclintfs = child.find(str(QName(ns, "AclInterfaces")))
        """
            In Multi-NPU platforms the mgmt intfs are defined only for the host not for individual asic
            There is just one mgmtintf node in the minigraph
            Get the mgmtintfs node first. We need mgmt intf to get mgmt ip in per asic dockers.
        """
        if mgmtintfs is None and child.find(str(QName(ns, "ManagementIPInterfaces"))) is not None:
            mgmtintfs = child.find(str(QName(ns, "ManagementIPInterfaces")))
        hostname = child.find(str(QName(ns, "Hostname")))
        if hostname.text.lower() != hname.lower():
            continue

        vni = vni_default
        vni_element = child.find(str(QName(ns, "VNI")))
        if vni_element != None:
            if vni_element.text.isdigit():
                vni = int(vni_element.text)
            else:
                print("VNI must be an integer (use default VNI %d instead)" % vni_default, file=sys.stderr) 

        ipintfs = child.find(str(QName(ns, "IPInterfaces")))
        intfs = {}
        for ipintf in ipintfs.findall(str(QName(ns, "IPInterface"))):
            intfalias = ipintf.find(str(QName(ns, "AttachTo"))).text
            intfname = port_alias_map.get(intfalias, intfalias)
            ipprefix = ipintf.find(str(QName(ns, "Prefix"))).text
            intfs[(intfname, ipprefix)] = {}

        lo_intfs =  parse_loopback_intf(child)

        mvrfConfigs = child.find(str(QName(ns, "MgmtVrfConfigs")))
        mvrf = {}
        if mvrfConfigs != None:
            mv = mvrfConfigs.find(str(QName(ns1, "MgmtVrfGlobal")))
            if mv != None:
                mvrf_en_flag = mv.find(str(QName(ns, "mgmtVrfEnabled"))).text
                mvrf["vrf_global"] = {"mgmtVrfEnabled": mvrf_en_flag}

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
        pc_members = {}
        intfs_inpc = [] # List to hold all the LAG member interfaces 
        for pcintf in pcintfs.findall(str(QName(ns, "PortChannel"))):
            pcintfname = pcintf.find(str(QName(ns, "Name"))).text
            pcintfmbr = pcintf.find(str(QName(ns, "AttachTo"))).text
            pcmbr_list = pcintfmbr.split(';')
            pc_intfs.append(pcintfname)
            for i, member in enumerate(pcmbr_list):
                pcmbr_list[i] = port_alias_map.get(member, member)
                intfs_inpc.append(pcmbr_list[i])
                pc_members[(pcintfname, pcmbr_list[i])] = {'NULL': 'NULL'}
            if pcintf.find(str(QName(ns, "Fallback"))) != None:
                pcs[pcintfname] = {'members': pcmbr_list, 'fallback': pcintf.find(str(QName(ns, "Fallback"))).text, 'min_links': str(int(math.ceil(len() * 0.75)))}
            else:
                pcs[pcintfname] = {'members': pcmbr_list, 'min_links': str(int(math.ceil(len(pcmbr_list) * 0.75)))}

        vlanintfs = child.find(str(QName(ns, "VlanInterfaces")))
        vlan_intfs = []
        vlans = {}
        vlan_members = {}
        vlantype_name = ""
        for vintf in vlanintfs.findall(str(QName(ns, "VlanInterface"))):
            vintfname = vintf.find(str(QName(ns, "Name"))).text
            vlanid = vintf.find(str(QName(ns, "VlanID"))).text
            vintfmbr = vintf.find(str(QName(ns, "AttachTo"))).text
            vlantype = vintf.find(str(QName(ns, "Type")))
            if vlantype != None:
                vlantype_name = vintf.find(str(QName(ns, "Type"))).text
            vmbr_list = vintfmbr.split(';')
            for i, member in enumerate(vmbr_list):
                vmbr_list[i] = port_alias_map.get(member, member)
                sonic_vlan_member_name = "Vlan%s" % (vlanid)
                if vlantype_name == "Tagged":
                    vlan_members[(sonic_vlan_member_name, vmbr_list[i])] = {'tagging_mode': 'tagged'}
                else:
                    vlan_members[(sonic_vlan_member_name, vmbr_list[i])] = {'tagging_mode': 'untagged'}

            vlan_attributes = {'vlanid': vlanid}

            # If this VLAN requires a DHCP relay agent, it will contain a <DhcpRelays> element
            # containing a list of DHCP server IPs
            vintf_node = vintf.find(str(QName(ns, "DhcpRelays")))
            if vintf_node is not None and vintf_node.text is not None:
                vintfdhcpservers = vintf_node.text
                vdhcpserver_list = vintfdhcpservers.split(';')
                vlan_attributes['dhcp_servers'] = vdhcpserver_list

            sonic_vlan_name = "Vlan%s" % vlanid
            if sonic_vlan_name != vintfname:
                vlan_attributes['alias'] = vintfname
            vlans[sonic_vlan_name] = vlan_attributes

        acls = {}
        for aclintf in aclintfs.findall(str(QName(ns, "AclInterface"))):
            if aclintf.find(str(QName(ns, "InAcl"))) is not None:
                aclname = aclintf.find(str(QName(ns, "InAcl"))).text.upper().replace(" ", "_").replace("-", "_")
                stage = "ingress"
            elif aclintf.find(str(QName(ns, "OutAcl"))) is not None:
                aclname = aclintf.find(str(QName(ns, "OutAcl"))).text.upper().replace(" ", "_").replace("-", "_")
                stage = "egress"
            else:
                system.exit("Error: 'AclInterface' must contain either an 'InAcl' or 'OutAcl' subelement.")
            aclattach = aclintf.find(str(QName(ns, "AttachTo"))).text.split(';')
            acl_intfs = []
            is_mirror = False
            is_mirror_v6 = False

            # TODO: Ensure that acl_intfs will only ever contain front-panel interfaces (e.g.,
            # maybe we should explicity ignore management and loopback interfaces?) because we
            # decide an ACL is a Control Plane ACL if acl_intfs is empty below.
            for member in aclattach:
                member = member.strip()
                if member in pcs:
                    # If try to attach ACL to a LAG interface then we shall add the LAG to
                    # to acl_intfs directly instead of break it into member ports, ACL attach
                    # to LAG will be applied to all the LAG members internally by SAI/SDK
                    acl_intfs.append(member)
                elif member in vlans:
                    acl_intfs.append(member)
                elif member in port_alias_map:
                    acl_intfs.append(port_alias_map[member])
                    # Give a warning if trying to attach ACL to a LAG member interface, correct way is to attach ACL to the LAG interface
                    if port_alias_map[member] in intfs_inpc:
                        print("Warning: ACL " + aclname + " is attached to a LAG member interface " + port_alias_map[member] + ", instead of LAG interface", file=sys.stderr)
                elif member.lower().startswith('erspan') or member.lower().startswith('egress_erspan'):
                    if member.lower().startswith('erspanv6') or member.lower().startswith('egress_erspanv6'):
                        is_mirror_v6 = True
                    else:
                        is_mirror = True
                    # Erspan session will be attached to all front panel ports
                    # initially. If panel ports is a member port of LAG, then
                    # the LAG will be added to acl table instead of the panel
                    # ports. Non-active ports will be removed from this list
                    # later after the rest of the minigraph has been parsed.
                    acl_intfs = pc_intfs[:]
                    for panel_port in port_alias_map.values():
                        # because of port_alias_asic_map we can have duplicate in port_alias_map
                        # so check if already present do not add
                        if panel_port not in intfs_inpc and panel_port not in acl_intfs:
                            acl_intfs.append(panel_port)
                    break
            if acl_intfs:
                acls[aclname] = {'policy_desc': aclname,
                                 'stage': stage,
                                 'ports': acl_intfs}
                if is_mirror:
                    acls[aclname]['type'] = 'MIRROR'
                elif is_mirror_v6:
                    acls[aclname]['type'] = 'MIRRORV6'
                else:
                    acls[aclname]['type'] = 'L3V6' if  'v6' in aclname.lower() else 'L3'
            else:
                # This ACL has no interfaces to attach to -- consider this a control plane ACL
                try:
                    aclservice = aclintf.find(str(QName(ns, "Type"))).text

                    # If we already have an ACL with this name and this ACL is bound to a different service,
                    # append the service to our list of services
                    if aclname in acls:
                        if acls[aclname]['type'] != 'CTRLPLANE':
                            print("Warning: ACL '%s' type mismatch. Not updating ACL." % aclname, file=sys.stderr)
                        elif acls[aclname]['services'] == aclservice:
                            print("Warning: ACL '%s' already contains service '%s'. Not updating ACL." % (aclname, aclservice), file=sys.stderr)
                        else:
                            acls[aclname]['services'].append(aclservice)
                    else:
                        acls[aclname] = {'policy_desc': aclname,
                                         'type': 'CTRLPLANE',
                                         'stage': stage,
                                         'services': [aclservice]}
                except:
                    print("Warning: Ignoring Control Plane ACL %s without type" % aclname, file=sys.stderr)

        return intfs, lo_intfs, mvrf, mgmt_intf, vlans, vlan_members, pcs, pc_members, acls, vni
    return None, None, None, None, None, None, None, None, None, None

def parse_host_loopback(dpg, hname):
    for child in dpg:
        hostname = child.find(str(QName(ns, "Hostname")))
        if hostname.text.lower() != hname.lower():
            continue
        lo_intfs = parse_loopback_intf(child)
        return lo_intfs

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
                if end_router.lower() == hname.lower():
                    bgp_sessions[start_peer.lower()] = {
                        'name': start_router,
                        'local_addr': end_peer.lower(),
                        'rrclient': rrclient,
                        'holdtime': holdtime,
                        'keepalive': keepalive,
                        'nhopself': nhopself
                    }
                elif start_router.lower() == hname.lower():
                    bgp_sessions[end_peer.lower()] = {
                        'name': end_router,
                        'local_addr': start_peer.lower(),
                        'rrclient': rrclient,
                        'holdtime': holdtime,
                        'keepalive': keepalive,
                        'nhopself': nhopself
                    }
        elif child.tag == str(QName(ns, "Routers")):
            for router in child.findall(str(QName(ns1, "BGPRouterDeclaration"))):
                asn = router.find(str(QName(ns1, "ASN"))).text
                hostname = router.find(str(QName(ns1, "Hostname"))).text
                if hostname.lower() == hname.lower():
                    myasn = asn
                    peers = router.find(str(QName(ns1, "Peers")))
                    for bgpPeer in peers.findall(str(QName(ns, "BGPPeer"))):
                        addr = bgpPeer.find(str(QName(ns, "Address"))).text
                        if bgpPeer.find(str(QName(ns1, "PeersRange"))) is not None: # FIXME: is better to check for type BGPPeerPassive
                            name = bgpPeer.find(str(QName(ns1, "Name"))).text
                            ip_range = bgpPeer.find(str(QName(ns1, "PeersRange"))).text
                            ip_range_group = ip_range.split(';') if ip_range and ip_range != "" else []
                            bgp_peers_with_range[name] = {
                                'name': name,
                                'ip_range': ip_range_group
                            }
                            if bgpPeer.find(str(QName(ns, "Address"))) is not None:
                                bgp_peers_with_range[name]['src_address'] = bgpPeer.find(str(QName(ns, "Address"))).text
                            if bgpPeer.find(str(QName(ns1, "PeerAsn"))) is not None:
                                bgp_peers_with_range[name]['peer_asn'] = bgpPeer.find(str(QName(ns1, "PeerAsn"))).text
                else:
                    for peer in bgp_sessions:
                        bgp_session = bgp_sessions[peer]
                        if hostname.lower() == bgp_session['name'].lower():
                            bgp_session['asn'] = asn

    bgp_monitors = { key: bgp_sessions[key] for key in bgp_sessions if 'asn' in bgp_sessions[key] and bgp_sessions[key]['name'] == 'BGPMonitor' }
    bgp_sessions = { key: bgp_sessions[key] for key in bgp_sessions if 'asn' in bgp_sessions[key] and int(bgp_sessions[key]['asn']) != 0 }

    return bgp_sessions, myasn, bgp_peers_with_range, bgp_monitors


def parse_meta(meta, hname):
    syslog_servers = []
    dhcp_servers = []
    ntp_servers = []
    tacacs_servers = []
    mgmt_routes = []
    erspan_dst = []
    deployment_id = None
    region = None
    cloudtype = None
    device_metas = meta.find(str(QName(ns, "Devices")))
    for device in device_metas.findall(str(QName(ns1, "DeviceMetadata"))):
        if device.find(str(QName(ns1, "Name"))).text.lower() == hname.lower():
            properties = device.find(str(QName(ns1, "Properties")))
            for device_property in properties.findall(str(QName(ns1, "DeviceProperty"))):
                name = device_property.find(str(QName(ns1, "Name"))).text
                value = device_property.find(str(QName(ns1, "Value"))).text
                value_group = value.strip().split(';') if value and value != "" else []
                if name == "DhcpResources":
                    dhcp_servers = value_group
                elif name == "NtpResources":
                    ntp_servers = value_group
                elif name == "SyslogResources":
                    syslog_servers = value_group
                elif name == "TacacsServer":
                    tacacs_servers = value_group
                elif name == "ForcedMgmtRoutes":
                    mgmt_routes = value_group
                elif name == "ErspanDestinationIpv4":
                    erspan_dst = value_group
                elif name == "DeploymentId":
                    deployment_id = value
                elif name == "Region":
                    region = value
                elif name == "CloudType":
                    cloudtype = value
    return syslog_servers, dhcp_servers, ntp_servers, tacacs_servers, mgmt_routes, erspan_dst, deployment_id, region, cloudtype


def parse_linkmeta(meta, hname):
    link = meta.find(str(QName(ns, "Link")))
    linkmetas = {}
    for linkmeta in link.findall(str(QName(ns1, "LinkMetadata"))):
        port = None
        fec_disabled = None

        # Sample: ARISTA05T1:Ethernet1/33;switch-t0:fortyGigE0/4
        key = linkmeta.find(str(QName(ns1, "Key"))).text
        endpoints = key.split(';')
        for endpoint in endpoints:
            t = endpoint.split(':')
            if len(t) == 2 and t[0].lower() == hname.lower():
                port = t[1]
                break
        else:
            # Cannot find a matching hname, something went wrong
            continue

        properties = linkmeta.find(str(QName(ns1, "Properties")))
        for device_property in properties.findall(str(QName(ns1, "DeviceProperty"))):
            name = device_property.find(str(QName(ns1, "Name"))).text
            value = device_property.find(str(QName(ns1, "Value"))).text
            if name == "FECDisabled":
                fec_disabled = value

        linkmetas[port] = {}
        if fec_disabled:
            linkmetas[port]["FECDisabled"] = fec_disabled
    return linkmetas


def parse_asic_meta(meta, hname):
    sub_role = None
    device_metas = meta.find(str(QName(ns, "Devices")))
    for device in device_metas.findall(str(QName(ns1, "DeviceMetadata"))):
        if device.find(str(QName(ns1, "Name"))).text.lower() == hname.lower():
            properties = device.find(str(QName(ns1, "Properties")))
            for device_property in properties.findall(str(QName(ns1, "DeviceProperty"))):
                name = device_property.find(str(QName(ns1, "Name"))).text
                value = device_property.find(str(QName(ns1, "Value"))).text
                if name == "SubRole":
                    sub_role = value
    return sub_role

def parse_deviceinfo(meta, hwsku):
    port_speeds = {}
    port_descriptions = {}
    for device_info in meta.findall(str(QName(ns, "DeviceInfo"))):
        dev_sku = device_info.find(str(QName(ns, "HwSku"))).text
        if dev_sku == hwsku:
            interfaces = device_info.find(str(QName(ns, "EthernetInterfaces"))).findall(str(QName(ns1, "EthernetInterface")))
            interfaces = interfaces + device_info.find(str(QName(ns, "ManagementInterfaces"))).findall(str(QName(ns1, "ManagementInterface")))
            for interface in interfaces:
                alias = interface.find(str(QName(ns, "InterfaceName"))).text
                speed = interface.find(str(QName(ns, "Speed"))).text
                desc  = interface.find(str(QName(ns, "Description")))
                if desc != None:
                    port_descriptions[port_alias_map.get(alias, alias)] = desc.text
                port_speeds[port_alias_map.get(alias, alias)] = speed
    return port_speeds, port_descriptions

# Function to check if IP address is present in the key. 
# If it is present, then the key would be a tuple.
def is_ip_prefix_in_key(key):
    return (isinstance(key, tuple))

# Special parsing for spine chassis frontend 
def parse_spine_chassis_fe(results, vni, lo_intfs, phyport_intfs, pc_intfs, pc_members, devices):
    chassis_vnet ='VnetFE'
    chassis_vxlan_tunnel = 'TunnelInt'
    chassis_vni = vni

    # Vxlan tunnel information
    lo_addr = '0.0.0.0'
    for lo in lo_intfs:
        lo_network = ipaddress.IPNetwork(lo[1])
        if lo_network.version == 4:
            lo_addr = str(lo_network.ip)
            break
    results['VXLAN_TUNNEL'] = {chassis_vxlan_tunnel: {
        'src_ip': lo_addr
    }}

    # Vnet information
    results['VNET'] = {chassis_vnet: {
        'vxlan_tunnel': chassis_vxlan_tunnel,
        'vni': chassis_vni
    }}

    # For each IP interface
    for intf in phyport_intfs:
        # A IP interface may have multiple entries. 
        # For example, "Ethernet0": {}", "Ethernet0|192.168.1.1": {}"
        # We only care about the one without IP information
        if is_ip_prefix_in_key(intf) == True:
            continue 
            
        neighbor_router = results['DEVICE_NEIGHBOR'][intf]['name']
            
        # If the neighbor router is an external router 
        if devices[neighbor_router]['type'] != chassis_backend_role:
            # Enslave the interface to a Vnet
            phyport_intfs[intf] = {'vnet_name': chassis_vnet}
           
    # For each port channel IP interface
    for pc_intf in pc_intfs:
        # A port channel IP interface may have multiple entries. 
        # For example, "Portchannel0": {}", "Portchannel0|192.168.1.1": {}"
        # We only care about the one without IP information
        if is_ip_prefix_in_key(pc_intf) == True:
            continue 

        intf_name = None 
        # Get a physical interface that belongs to this port channel         
        for pc_member in pc_members:
            if pc_member[0] == pc_intf:
                intf_name = pc_member[1]
                break

        if intf_name == None:
            print('Warning: cannot find any interfaces that belong to %s' % (pc_intf), file=sys.stderr)
            continue

        # Get the neighbor router of this port channel interface
        neighbor_router = results['DEVICE_NEIGHBOR'][intf_name]['name']

        # If the neighbor router is an external router 
        if devices[neighbor_router]['type'] != chassis_backend_role:
            # Enslave the port channel interface to a Vnet
            pc_intfs[pc_intf] = {'vnet_name': chassis_vnet}        

###############################################################################
#
# Post-processing functions
#
###############################################################################

def filter_acl_table_bindings(acls, neighbors, port_channels, sub_role):
    filter_acls = {}
    
    # If the asic role is BackEnd no ACL Table (Ctrl/Data/Everflow) is binded.
    # This will be applicable in Multi-NPU Platforms.
    
    if sub_role == BACKEND_ASIC_SUB_ROLE:
        return filter_acls

    front_port_channel_intf = []
   
    # Get the front panel port channel. It will use port_alias_asic_map
    # which will get populated from port_config.ini for Multi-NPU 
    # architecture
    for port_channel_intf in port_channels:
        backend_port_channel = any(lag_member in port_alias_asic_map \
                                   and lag_member.startswith(backplane_prefix()) \
                                   for lag_member in port_channels[port_channel_intf]['members'])
        if not backend_port_channel:
            front_port_channel_intf.append(port_channel_intf)

    for acl_table, group_params in acls.items():
        group_type = group_params.get('type', None)
        filter_acls[acl_table] = acls[acl_table]

        # For Control Plane and Data ACL no filtering is needed
        # Control Plane ACL has no Interface associated and
        # Data Plane ACL Interface are attached via minigraph
        # AclInterface.
        if group_type != 'MIRROR' and group_type != 'MIRRORV6':
            continue

        # Filters out back-panel ports from the binding list for Everflow (Mirror)
        # ACL tables. We define an "back-panel" port as one that is a member of a
        # port channel connected to back asic or directly connected to back asic.
        # This will be applicable in Multi-NPU Platforms.
        front_panel_ports = []
        for port in group_params.get('ports', []):
            if port in port_alias_asic_map and port.startswith(backplane_prefix()):
                continue
            if port in port_channels and port not in front_port_channel_intf:
                continue
            front_panel_ports.append(port)
        
        # Filters out inactive front-panel ports from the binding list for mirror
        # ACL tables. We define an "active" port as one that is a member of a
        # front pannel port channel or one that is connected to a neighboring device via front panel port.
        active_ports = [port for port in front_panel_ports if port in neighbors.keys() or port in front_port_channel_intf]
        
        if not active_ports:
            print('Warning: mirror table {} in ACL_TABLE does not have any ports bound to it'.format(acl_table), file=sys.stderr)

        filter_acls[acl_table]['ports'] = active_ports

    return filter_acls

def enable_internal_bgp_session(bgp_sessions, filename, asic_name):
    '''
    In Multi-NPU session the internal sessions will always be up.
    So adding the admin-status 'up' configuration to bgp sessions
    BGP session between FrontEnd and BackEnd Asics are internal bgp sessions
    '''
    local_sub_role = parse_asic_sub_role(filename, asic_name)

    for peer_ip in bgp_sessions.keys():
        peer_name = bgp_sessions[peer_ip]['name']
        peer_sub_role = parse_asic_sub_role(filename, peer_name)
        if ((local_sub_role == FRONTEND_ASIC_SUB_ROLE and peer_sub_role == BACKEND_ASIC_SUB_ROLE) or
            (local_sub_role == BACKEND_ASIC_SUB_ROLE and peer_sub_role == FRONTEND_ASIC_SUB_ROLE)):
            bgp_sessions[peer_ip].update({'admin_status': 'up'})

###############################################################################
#
# Main functions
#
###############################################################################
def parse_xml(filename, platform=None, port_config_file=None, asic_name=None, hwsku_config_file=None):
    """ Parse minigraph xml file.

    Keyword arguments:
    filename -- minigraph file name
    platform -- device platform
    port_config_file -- port config file name
    asic_name -- asic name; to parse multi-asic device minigraph to 
    generate asic specific configuration.
     """

    root = ET.parse(filename).getroot()

    u_neighbors = None
    u_devices = None
    hwsku = None
    bgp_sessions = None
    bgp_monitors = []
    bgp_asn = None
    intfs = None
    vlan_intfs = None
    pc_intfs = None
    vlans = None
    vlan_members = None
    pcs = None
    mgmt_intf = None
    lo_intfs = None
    neighbors = None
    devices = None
    sub_role = None
    docker_routing_config_mode = "separated"
    port_speeds_default = {}
    port_speed_png = {}
    port_descriptions = {}
    console_ports = {}
    syslog_servers = []
    dhcp_servers = []
    ntp_servers = []
    tacacs_servers = []
    mgmt_routes = []
    erspan_dst = []
    bgp_peers_with_range = None
    deployment_id = None
    region = None
    cloudtype = None
    hostname = None
    linkmetas = {}
    host_lo_intfs = None

    # hostname is the asic_name, get the asic_id from the asic_name
    if asic_name is not None:
        asic_id = get_asic_id_from_name(asic_name)
    else:
        asic_id = None

    hwsku_qn = QName(ns, "HwSku")
    hostname_qn = QName(ns, "Hostname")
    docker_routing_config_mode_qn = QName(ns, "DockerRoutingConfigMode")
    for child in root:
        if child.tag == str(hwsku_qn):
            hwsku = child.text
        if child.tag == str(hostname_qn):
            hostname = child.text
        if child.tag == str(docker_routing_config_mode_qn):
            docker_routing_config_mode = child.text

    (ports, alias_map, alias_asic_map) = get_port_config(hwsku=hwsku, platform=platform, port_config_file=port_config_file, asic=asic_id, hwsku_config_file=hwsku_config_file)
    port_alias_map.update(alias_map)
    port_alias_asic_map.update(alias_asic_map)

    for child in root:
        if asic_name is None:
            if child.tag == str(QName(ns, "DpgDec")):
                (intfs, lo_intfs, mvrf, mgmt_intf, vlans, vlan_members, pcs, pc_members, acls, vni) = parse_dpg(child, hostname)
            elif child.tag == str(QName(ns, "CpgDec")):
                (bgp_sessions, bgp_asn, bgp_peers_with_range, bgp_monitors) = parse_cpg(child, hostname)
            elif child.tag == str(QName(ns, "PngDec")):
                (neighbors, devices, console_dev, console_port, mgmt_dev, mgmt_port, port_speed_png, console_ports) = parse_png(child, hostname)
            elif child.tag == str(QName(ns, "UngDec")):
                (u_neighbors, u_devices, _, _, _, _, _, _) = parse_png(child, hostname)
            elif child.tag == str(QName(ns, "MetadataDeclaration")):
                (syslog_servers, dhcp_servers, ntp_servers, tacacs_servers, mgmt_routes, erspan_dst, deployment_id, region, cloudtype) = parse_meta(child, hostname)
            elif child.tag == str(QName(ns, "LinkMetadataDeclaration")):
                linkmetas = parse_linkmeta(child, hostname)
            elif child.tag == str(QName(ns, "DeviceInfos")):
                (port_speeds_default, port_descriptions) = parse_deviceinfo(child, hwsku)
        else:
            if child.tag == str(QName(ns, "DpgDec")):
                (intfs, lo_intfs, mvrf, mgmt_intf, vlans, vlan_members, pcs, pc_members, acls, vni) = parse_dpg(child, asic_name)
                host_lo_intfs = parse_host_loopback(child, hostname)
            elif child.tag == str(QName(ns, "CpgDec")):
                (bgp_sessions, bgp_asn, bgp_peers_with_range, bgp_monitors) = parse_cpg(child, asic_name)
                enable_internal_bgp_session(bgp_sessions, filename, asic_name)
            elif child.tag == str(QName(ns, "PngDec")):
                (neighbors, devices, port_speed_png) = parse_asic_png(child, asic_name, hostname)
            elif child.tag == str(QName(ns, "MetadataDeclaration")):
                (sub_role) = parse_asic_meta(child, asic_name)
            elif child.tag == str(QName(ns, "LinkMetadataDeclaration")):
                linkmetas = parse_linkmeta(child, hostname)
            elif child.tag == str(QName(ns, "DeviceInfos")):
                (port_speeds_default, port_descriptions) = parse_deviceinfo(child, hwsku)

    # set the host device type in asic metadata also
    device_type = [devices[key]['type'] for key in devices if key.lower() == hostname.lower()][0]
    if asic_name is None:
        current_device = [devices[key] for key in devices if key.lower() == hostname.lower()][0]
    else:
        current_device = [devices[key] for key in devices if key.lower() == asic_name.lower()][0]

    results = {}
    results['DEVICE_METADATA'] = {'localhost': {
        'bgp_asn': bgp_asn,
        'deployment_id': deployment_id,
        'region': region,
        'cloudtype': cloudtype,
        'docker_routing_config_mode': docker_routing_config_mode,
        'hostname': hostname,
        'hwsku': hwsku,
        'type': device_type
        }
    }
    # for this hostname, if sub_role is defined, add sub_role in 
    # device_metadata
    if sub_role is not None:
        current_device['sub_role'] = sub_role
        results['DEVICE_METADATA']['localhost']['sub_role'] =  sub_role
        results['DEVICE_METADATA']['localhost']['asic_name'] =  asic_name
    results['BGP_NEIGHBOR'] = bgp_sessions
    results['BGP_MONITORS'] = bgp_monitors
    results['BGP_PEER_RANGE'] = bgp_peers_with_range
    if mgmt_routes:
        # TODO: differentiate v4 and v6
        iter(mgmt_intf.values()).next()['forced_mgmt_routes'] = mgmt_routes
    results['MGMT_PORT'] = {}
    results['MGMT_INTERFACE'] = {}
    mgmt_intf_count = 0
    mgmt_alias_reverse_mapping = {}
    for key in mgmt_intf:
        alias = key[0]
        if alias in mgmt_alias_reverse_mapping:
            name = mgmt_alias_reverse_mapping[alias]
        else:
            name = 'eth' + str(mgmt_intf_count)
            mgmt_intf_count += 1
            mgmt_alias_reverse_mapping[alias] = name
        results['MGMT_PORT'][name] = {'alias': alias, 'admin_status': 'up'}
        if alias in port_speeds_default:
            results['MGMT_PORT'][name]['speed'] = port_speeds_default[alias]
        results['MGMT_INTERFACE'][(name, key[1])] = mgmt_intf[key]
    results['LOOPBACK_INTERFACE'] = {}
    for lo_intf in lo_intfs:
        results['LOOPBACK_INTERFACE'][lo_intf] = lo_intfs[lo_intf]
        results['LOOPBACK_INTERFACE'][lo_intf[0]] = {}

    if host_lo_intfs is not None:
        for host_lo_intf in host_lo_intfs:
            results['LOOPBACK_INTERFACE'][host_lo_intf] = host_lo_intfs[host_lo_intf]
            results['LOOPBACK_INTERFACE'][host_lo_intf[0]] = {}

    results['MGMT_VRF_CONFIG'] = mvrf

    phyport_intfs = {}
    vlan_intfs = {}
    pc_intfs = {}
    vlan_invert_mapping = { v['alias']:k for k,v in vlans.items() if 'alias' in v }
    vlan_sub_intfs = {}

    for intf in intfs:
        if intf[0][0:4] == 'Vlan':
            vlan_intfs[intf] = {}
            vlan_intfs[intf[0]] = {}
        elif intf[0] in vlan_invert_mapping:
            vlan_intfs[(vlan_invert_mapping[intf[0]], intf[1])] = {}
            vlan_intfs[vlan_invert_mapping[intf[0]]] = {}
        elif intf[0][0:11] == 'PortChannel':
            pc_intfs[intf] = {}
            pc_intfs[intf[0]] = {}
        else:
            phyport_intfs[intf] = {}
            phyport_intfs[intf[0]] = {}

    results['INTERFACE'] = phyport_intfs
    results['VLAN_INTERFACE'] = vlan_intfs

    for port_name in port_speeds_default:
        # ignore port not in port_config.ini
        if port_name not in ports:
            continue

        ports.setdefault(port_name, {})['speed'] = port_speeds_default[port_name]

    for port_name in port_speed_png:
        # not consider port not in port_config.ini
        # If no port_config_file is found ports is empty so ignore this error
        if port_config_file is not None:
            if port_name not in ports:
                print("Warning: ignore interface '%s' as it is not in the port_config.ini" % port_name, file=sys.stderr)
                continue

        ports.setdefault(port_name, {})['speed'] = port_speed_png[port_name]

    for port_name, port in list(ports.items()):
        # get port alias from port_config.ini
        alias = port.get('alias', port_name)
        # generate default 100G FEC
        # Note: FECDisabled only be effective on 100G port right now
        if port.get('speed') == '100000' and linkmetas.get(alias, {}).get('FECDisabled', '').lower() != 'true':
            port['fec'] = 'rs'

    # set port description if parsed from deviceinfo
    for port_name in port_descriptions:
        # ignore port not in port_config.ini
        if port_name not in ports:
            continue

        ports.setdefault(port_name, {})['description'] = port_descriptions[port_name]

    for port_name, port in ports.items():
        if not port.get('description'):
            if port_name in neighbors:
                # for the ports w/o description set it to neighbor name:port
                port['description'] = "%s:%s" % (neighbors[port_name]['name'], neighbors[port_name]['port'])
            else:
                # for the ports w/o neighbor info, set it to port alias
                port['description'] = port.get('alias', port_name)

    # set default port MTU as 9100
    for port in ports.values():
        port['mtu'] = '9100'

    # asymmetric PFC is disabled by default
    for port in ports.values():
        port['pfc_asym'] = 'off'

    # set physical port default admin status up
    for port in phyport_intfs:
        if port[0] in ports:
            ports.get(port[0])['admin_status'] = 'up'

    for member in list(pc_members.keys()) + list(vlan_members.keys()):
        port = ports.get(member[1])
        if port:
            port['admin_status'] = 'up'

    for port in neighbors.keys():
        if port in ports.keys():
            # make all neighbors connected ports to 'admin_up'
            ports[port]['admin_status'] = 'up'

    results['PORT'] = ports
    results['CONSOLE_PORT'] = console_ports

    if port_config_file:
        port_set = set(ports.keys())
        for (pc_name, mbr_map) in pcs.items():
            # remove portchannels that contain ports not existing in port_config.ini
            # when port_config.ini exists
            if not set(mbr_map['members']).issubset(port_set):
                print("Warning: ignore '%s' as part of its member interfaces is not in the port_config.ini" % pc_name, file=sys.stderr)
                del pcs[pc_name]

    # set default port channel MTU as 9100 and admin status up
    for pc in pcs.values():
        pc['mtu'] = '9100'
        pc['admin_status'] = 'up'

    results['PORTCHANNEL'] = pcs
    results['PORTCHANNEL_MEMBER'] = pc_members

    for pc_intf in pc_intfs.keys():
        # remove portchannels not in PORTCHANNEL dictionary
        if isinstance(pc_intf, tuple) and pc_intf[0] not in pcs:
            print("Warning: ignore '%s' interface '%s' as '%s' is not in the valid PortChannel list" % (pc_intf[0], pc_intf[1], pc_intf[0]), file=sys.stderr)
            del pc_intfs[pc_intf]
            pc_intfs.pop(pc_intf[0], None)

    results['PORTCHANNEL_INTERFACE'] = pc_intfs

    if current_device['type'] in backend_device_types:
        del results['INTERFACE']
        del results['PORTCHANNEL_INTERFACE']

        for intf in phyport_intfs.keys():
            if isinstance(intf, tuple):
                intf_info = list(intf)
                intf_info[0] = intf_info[0] + VLAN_SUB_INTERFACE_SEPARATOR + VLAN_SUB_INTERFACE_VLAN_ID
                sub_intf = tuple(intf_info)
                vlan_sub_intfs[sub_intf] = {}
            else:
                sub_intf = intf + VLAN_SUB_INTERFACE_SEPARATOR + VLAN_SUB_INTERFACE_VLAN_ID
                vlan_sub_intfs[sub_intf] = {"admin_status" : "up"}

        for pc_intf in pc_intfs.keys():
            if isinstance(pc_intf, tuple):
                pc_intf_info = list(pc_intf)
                pc_intf_info[0] = pc_intf_info[0] + VLAN_SUB_INTERFACE_SEPARATOR + VLAN_SUB_INTERFACE_VLAN_ID
                sub_intf = tuple(pc_intf_info)
                vlan_sub_intfs[sub_intf] = {}
            else:
                sub_intf = pc_intf + VLAN_SUB_INTERFACE_SEPARATOR + VLAN_SUB_INTERFACE_VLAN_ID
                vlan_sub_intfs[sub_intf] = {"admin_status" : "up"}

        results['VLAN_SUB_INTERFACE'] = vlan_sub_intfs

    results['VLAN'] = vlans
    results['VLAN_MEMBER'] = vlan_members

    for nghbr in neighbors.keys():
        # remove port not in port_config.ini
        if nghbr not in ports:
            if port_config_file is not None:
                print("Warning: ignore interface '%s' in DEVICE_NEIGHBOR as it is not in the port_config.ini" % nghbr, file=sys.stderr)
            del neighbors[nghbr]
    results['DEVICE_NEIGHBOR'] = neighbors
    if asic_name is None:
        results['DEVICE_NEIGHBOR_METADATA'] = { key:devices[key] for key in devices if key.lower() != hostname.lower() }
    else:
        results['DEVICE_NEIGHBOR_METADATA'] = { key:devices[key] for key in devices if key in {device['name'] for device in neighbors.values()} }
    results['SYSLOG_SERVER'] = dict((item, {}) for item in syslog_servers)
    results['DHCP_SERVER'] = dict((item, {}) for item in dhcp_servers)
    results['NTP_SERVER'] = dict((item, {}) for item in ntp_servers)
    results['TACPLUS_SERVER'] = dict((item, {'priority': '1', 'tcp_port': '49'}) for item in tacacs_servers)
    results['ACL_TABLE'] = filter_acl_table_bindings(acls, neighbors, pcs, sub_role)
    results['FEATURE'] = {
        'telemetry': {
            'status': 'enabled'
        }
    }
    results['TELEMETRY'] = {
        'gnmi': {
            'client_auth': 'true',
            'port': '50051',
            'log_level': '2'
        },
        'certs': {
            'server_crt': '/etc/sonic/telemetry/streamingtelemetryserver.cer',
            'server_key': '/etc/sonic/telemetry/streamingtelemetryserver.key',
            'ca_crt': '/etc/sonic/telemetry/dsmsroot.cer'
        }
    }
    results['RESTAPI'] = {
        'config': {
            'client_auth': 'true',
            'allow_insecure': 'false',
            'log_level': 'trace'
        },
        'certs': {
            'server_crt': '/etc/sonic/credentials/restapiserver.crt',
            'server_key': '/etc/sonic/credentials/restapiserver.key',
            'client_ca_crt': '/etc/sonic/credentials/restapiclient.crt',
            'client_crt_cname': 'client.restapi.sonic'
        }
    }
    # Do not configure the minigraph's mirror session, which is currently unused
    # mirror_sessions = {}
    # if erspan_dst:
    #     lo_addr = '0.0.0.0'
    #     for lo in lo_intfs:
    #         lo_network = ipaddress.IPNetwork(lo[1])
    #         if lo_network.version == 4:
    #             lo_addr = str(lo_network.ip)
    #             break
    #     count = 0
    #     for dst in erspan_dst:
    #         mirror_sessions['everflow{}'.format(count)] = {"dst_ip": dst, "src_ip": lo_addr}
    #         count += 1
    #     results['MIRROR_SESSION'] = mirror_sessions

    # Special parsing for spine chassis frontend routers
    if current_device['type'] == spine_chassis_frontend_role:
        parse_spine_chassis_fe(results, vni, lo_intfs, phyport_intfs, pc_intfs, pc_members, devices)

    return results


def parse_device_desc_xml(filename):
    root = ET.parse(filename).getroot()
    (lo_prefix, mgmt_prefix, hostname, hwsku, d_type, _) = parse_device(root)

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

def parse_asic_sub_role(filename, asic_name):
    if not os.path.isfile(filename):
        return None
    root = ET.parse(filename).getroot()
    for child in root:
        if child.tag == str(QName(ns, "MetadataDeclaration")):
            sub_role = parse_asic_meta(child, asic_name)
            return sub_role

port_alias_map = {}
port_alias_asic_map = {}


def print_parse_xml(filename):
    results = parse_xml(filename)
    print((json.dumps(results, indent=3, cls=minigraph_encoder)))

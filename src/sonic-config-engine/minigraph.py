#!/usr/bin/env python
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

"""minigraph.py
version_added: "1.9"
author: Guohan Lu (gulv@microsoft.com)
short_description: Parse minigraph xml file and device description xml file
"""

ns = "Microsoft.Search.Autopilot.Evolution"
ns1 = "http://schemas.datacontract.org/2004/07/Microsoft.Search.Autopilot.Evolution"
ns2 = "Microsoft.Search.Autopilot.NetMux"
ns3 = "http://www.w3.org/2001/XMLSchema-instance"

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
                    if port_alias_map.has_key(endport):
                        endport = port_alias_map[endport]
                    neighbors[endport] = {'name': startdevice, 'port': startport}
                    if bandwidth:
                        port_speeds[endport] = bandwidth
                else:
                    if port_alias_map.has_key(startport):
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


def parse_dpg(dpg, hname):
    for child in dpg:
        hostname = child.find(str(QName(ns, "Hostname")))
        if hostname.text.lower() != hname.lower():
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
        for vintf in vlanintfs.findall(str(QName(ns, "VlanInterface"))):
            vintfname = vintf.find(str(QName(ns, "Name"))).text
            vlanid = vintf.find(str(QName(ns, "VlanID"))).text
            vintfmbr = vintf.find(str(QName(ns, "AttachTo"))).text
            vmbr_list = vintfmbr.split(';')
            for i, member in enumerate(vmbr_list):
                vmbr_list[i] = port_alias_map.get(member, member)
                sonic_vlan_member_name = "Vlan%s" % (vlanid)
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

        aclintfs = child.find(str(QName(ns, "AclInterfaces")))
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
                if pcs.has_key(member):
                    # If try to attach ACL to a LAG interface then we shall add the LAG to
                    # to acl_intfs directly instead of break it into member ports, ACL attach
                    # to LAG will be applied to all the LAG members internally by SAI/SDK
                    acl_intfs.append(member)
                elif vlans.has_key(member):
                    acl_intfs.append(member)
                elif port_alias_map.has_key(member):
                    acl_intfs.append(port_alias_map[member])
                    # Give a warning if trying to attach ACL to a LAG member interface, correct way is to attach ACL to the LAG interface
                    if port_alias_map[member] in intfs_inpc:
                        print >> sys.stderr, "Warning: ACL " + aclname + " is attached to a LAG member interface " + port_alias_map[member] + ", instead of LAG interface"
                elif member.lower().startswith('erspan'):
                    if member.lower().startswith('erspanv6'):
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
                        if panel_port not in intfs_inpc:
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
                            print >> sys.stderr, "Warning: ACL '%s' type mismatch. Not updating ACL." % aclname
                        elif acls[aclname]['services'] == aclservice:
                            print >> sys.stderr, "Warning: ACL '%s' already contains service '%s'. Not updating ACL." % (aclname, aclservice)
                        else:
                            acls[aclname]['services'].append(aclservice)
                    else:
                        acls[aclname] = {'policy_desc': aclname,
                                         'type': 'CTRLPLANE',
                                         'stage': stage,
                                         'services': [aclservice]}
                except:
                    print >> sys.stderr, "Warning: Ignoring Control Plane ACL %s without type" % aclname

        return intfs, lo_intfs, mgmt_intf, vlans, vlan_members, pcs, pc_members, acls
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
                if end_router.lower() == hname.lower():
                    bgp_sessions[start_peer.lower()] = {
                        'name': start_router,
                        'local_addr': end_peer.lower(),
                        'rrclient': rrclient,
                        'holdtime': holdtime,
                        'keepalive': keepalive,
                        'nhopself': nhopself
                    }
                else:
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
    bgp_monitors = { key: bgp_sessions[key] for key in bgp_sessions if bgp_sessions[key].has_key('asn') and bgp_sessions[key]['name'] == 'BGPMonitor' }
    bgp_sessions = { key: bgp_sessions[key] for key in bgp_sessions if bgp_sessions[key].has_key('asn') and int(bgp_sessions[key]['asn']) != 0 }

    return bgp_sessions, myasn, bgp_peers_with_range, bgp_monitors


def parse_meta(meta, hname):
    syslog_servers = []
    dhcp_servers = []
    ntp_servers = []
    tacacs_servers = []
    mgmt_routes = []
    erspan_dst = []
    deployment_id = None
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
    return syslog_servers, dhcp_servers, ntp_servers, tacacs_servers, mgmt_routes, erspan_dst, deployment_id


def parse_linkmeta(meta, hname):
    link = meta.find(str(QName(ns, "Link")))
    linkmetas = {}
    for linkmeta in link.findall(str(QName(ns1, "LinkMetadata"))):
        port = None
        fec_disabled = None
        auto_negotiation = None

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
            elif name == "AutoNegotiation":
                auto_negotiation = value

        linkmetas[port] = {}
        if fec_disabled:
            linkmetas[port]["FECDisabled"] = fec_disabled
        if auto_negotiation:
            linkmetas[port]["AutoNegotiation"] = auto_negotiation
    return linkmetas


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

###############################################################################
#
# Post-processing functions
#
###############################################################################

def filter_acl_mirror_table_bindings(acls, neighbors, port_channels):
    """
        Filters out inactive front-panel ports from the binding list for mirror
        ACL tables. We define an "active" port as one that is a member of a
        port channel or one that is connected to a neighboring device.
    """

    for acl_table, group_params in acls.iteritems():
        group_type = group_params.get('type', None)

        if group_type != 'MIRROR' and group_type != 'MIRRORV6':
            continue

        active_ports = [ port for port in group_params.get('ports', []) if port in neighbors.keys() or port in port_channels ]

        if not active_ports:
            print >> sys.stderr, 'Warning: mirror table {} in ACL_TABLE does not have any ports bound to it'.format(acl_table)

        acls[acl_table]['ports'] = active_ports

    return acls

###############################################################################
#
# Main functions
#
###############################################################################

def parse_xml(filename, platform=None, port_config_file=None):
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
    lo_intf = None
    neighbors = None
    devices = None
    hostname = None
    docker_routing_config_mode = "unified"
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
    linkmetas = {}

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

    (ports, alias_map) = get_port_config(hwsku, platform, port_config_file)
    port_alias_map.update(alias_map)
    for child in root:
        if child.tag == str(QName(ns, "DpgDec")):
            (intfs, lo_intfs, mgmt_intf, vlans, vlan_members, pcs, pc_members, acls) = parse_dpg(child, hostname)
        elif child.tag == str(QName(ns, "CpgDec")):
            (bgp_sessions, bgp_asn, bgp_peers_with_range, bgp_monitors) = parse_cpg(child, hostname)
        elif child.tag == str(QName(ns, "PngDec")):
            (neighbors, devices, console_dev, console_port, mgmt_dev, mgmt_port, port_speed_png, console_ports) = parse_png(child, hostname)
        elif child.tag == str(QName(ns, "UngDec")):
            (u_neighbors, u_devices, _, _, _, _, _, _) = parse_png(child, hostname)
        elif child.tag == str(QName(ns, "MetadataDeclaration")):
            (syslog_servers, dhcp_servers, ntp_servers, tacacs_servers, mgmt_routes, erspan_dst, deployment_id) = parse_meta(child, hostname)
        elif child.tag == str(QName(ns, "LinkMetadataDeclaration")):
            linkmetas = parse_linkmeta(child, hostname)
        elif child.tag == str(QName(ns, "DeviceInfos")):
            (port_speeds_default, port_descriptions) = parse_deviceinfo(child, hwsku)

    current_device = [devices[key] for key in devices if key.lower() == hostname.lower()][0]
    results = {}
    results['DEVICE_METADATA'] = {'localhost': {
        'bgp_asn': bgp_asn,
        'deployment_id': deployment_id,
        'docker_routing_config_mode': docker_routing_config_mode,
        'hostname': hostname,
        'hwsku': hwsku,
        'type': current_device['type']
        }}
    results['BGP_NEIGHBOR'] = bgp_sessions
    results['BGP_MONITORS'] = bgp_monitors
    results['BGP_PEER_RANGE'] = bgp_peers_with_range
    if mgmt_routes:
        # TODO: differentiate v4 and v6
        mgmt_intf.itervalues().next()['forced_mgmt_routes'] = mgmt_routes
    results['MGMT_PORT'] = {}
    results['MGMT_INTERFACE'] = {}
    mgmt_intf_count = 0
    mgmt_alias_reverse_mapping = {}
    for key in mgmt_intf:
        alias = key[0]
        if mgmt_alias_reverse_mapping.has_key(alias):
            name = mgmt_alias_reverse_mapping[alias]
        else:
            name = 'eth' + str(mgmt_intf_count)
            mgmt_intf_count += 1
            mgmt_alias_reverse_mapping[alias] = name
        results['MGMT_PORT'][name] = {'alias': alias, 'admin_status': 'up'}
        if alias in port_speeds_default:
            results['MGMT_PORT'][name]['speed'] = port_speeds_default[alias]
        results['MGMT_INTERFACE'][(name, key[1])] = mgmt_intf[key]
    results['LOOPBACK_INTERFACE'] = lo_intfs

    phyport_intfs = {}
    vlan_intfs = {}
    pc_intfs = {}
    vlan_invert_mapping = { v['alias']:k for k,v in vlans.items() if v.has_key('alias') }

    for intf in intfs:
        if intf[0][0:4] == 'Vlan':
            vlan_intfs[intf] = {}
        elif vlan_invert_mapping.has_key(intf[0]):
            vlan_intfs[(vlan_invert_mapping[intf[0]], intf[1])] = {}
        elif intf[0][0:11] == 'PortChannel':
            pc_intfs[intf] = {}
        else:
            phyport_intfs[intf] = {}

    results['INTERFACE'] = phyport_intfs
    results['VLAN_INTERFACE'] = vlan_intfs

    for port_name in port_speeds_default:
        # ignore port not in port_config.ini
        if not ports.has_key(port_name):
            continue

        ports.setdefault(port_name, {})['speed'] = port_speeds_default[port_name]

    for port_name in port_speed_png:
        # not consider port not in port_config.ini
        if port_name not in ports:
            print >> sys.stderr, "Warning: ignore interface '%s' as it is not in the port_config.ini" % port_name
            continue

        ports.setdefault(port_name, {})['speed'] = port_speed_png[port_name]

    for port_name, port in ports.items():
        # get port alias from port_config.ini
        alias = port.get('alias', port_name)
        # generate default 100G FEC
        # Note: FECDisabled only be effective on 100G port right now
        if port.get('speed') == '100000' and linkmetas.get(alias, {}).get('FECDisabled', '').lower() != 'true':
            port['fec'] = 'rs'

        # If AutoNegotiation is available in the minigraph, we override any value we may have received from port_config.ini
        autoneg = linkmetas.get(alias, {}).get('AutoNegotiation')
        if autoneg:
            port['autoneg'] = '1' if autoneg.lower() == 'true' else '0'

    # set port description if parsed from deviceinfo
    for port_name in port_descriptions:
        # ignore port not in port_config.ini
        if not ports.has_key(port_name):
            continue

        ports.setdefault(port_name, {})['description'] = port_descriptions[port_name]

    for port_name, port in ports.items():
        if not port.get('description'):
            if neighbors.has_key(port_name):
                # for the ports w/o description set it to neighbor name:port
                port['description'] = "%s:%s" % (neighbors[port_name]['name'], neighbors[port_name]['port'])
            else:
                # for the ports w/o neighbor info, set it to port alias
                port['description'] = port.get('alias', port_name)

    # set default port MTU as 9100
    for port in ports.itervalues():
        port['mtu'] = '9100'

    # asymmetric PFC is disabled by default
    for port in ports.itervalues():
        port['pfc_asym'] = 'off'

    # set physical port default admin status up
    for port in phyport_intfs:
        if port[0] in ports:
            ports.get(port[0])['admin_status'] = 'up'

    for member in pc_members.keys() + vlan_members.keys():
        port = ports.get(member[1])
        if port:
            port['admin_status'] = 'up'

    results['PORT'] = ports
    results['CONSOLE_PORT'] = console_ports

    if port_config_file:
        port_set = set(ports.keys())
        for (pc_name, mbr_map) in pcs.items():
            # remove portchannels that contain ports not existing in port_config.ini
            # when port_config.ini exists
            if not set(mbr_map['members']).issubset(port_set):
                print >> sys.stderr, "Warning: ignore '%s' as part of its member interfaces is not in the port_config.ini" % pc_name
                del pcs[pc_name]

    # set default port channel MTU as 9100 and admin status up
    for pc in pcs.itervalues():
        pc['mtu'] = '9100'
        pc['admin_status'] = 'up'

    results['PORTCHANNEL'] = pcs
    results['PORTCHANNEL_MEMBER'] = pc_members

    for pc_intf in pc_intfs.keys():
        # remove portchannels not in PORTCHANNEL dictionary
        if pc_intf[0] not in pcs:
            print >> sys.stderr, "Warning: ignore '%s' interface '%s' as '%s' is not in the valid PortChannel list" % (pc_intf[0], pc_intf[1], pc_intf[0])
            del pc_intfs[pc_intf]

    results['PORTCHANNEL_INTERFACE'] = pc_intfs

    results['VLAN'] = vlans
    results['VLAN_MEMBER'] = vlan_members

    for nghbr in neighbors.keys():
        # remove port not in port_config.ini
        if nghbr not in ports:
            print >> sys.stderr, "Warning: ignore interface '%s' in DEVICE_NEIGHBOR as it is not in the port_config.ini" % nghbr
            del neighbors[nghbr]

    results['DEVICE_NEIGHBOR'] = neighbors
    results['DEVICE_NEIGHBOR_METADATA'] = { key:devices[key] for key in devices if key.lower() != hostname.lower() }
    results['SYSLOG_SERVER'] = dict((item, {}) for item in syslog_servers)
    results['DHCP_SERVER'] = dict((item, {}) for item in dhcp_servers)
    results['NTP_SERVER'] = dict((item, {}) for item in ntp_servers)
    results['TACPLUS_SERVER'] = dict((item, {'priority': '1', 'tcp_port': '49'}) for item in tacacs_servers)

    results['ACL_TABLE'] = filter_acl_mirror_table_bindings(acls, neighbors, pcs)

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


port_alias_map = {}


def print_parse_xml(filename):
    results = parse_xml(filename)
    print(json.dumps(results, indent=3, cls=minigraph_encoder))

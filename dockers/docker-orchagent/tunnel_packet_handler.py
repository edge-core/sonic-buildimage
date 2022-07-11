#! /usr/bin/env python3
"""
Adds neighbor to kernel for undeliverable tunnel packets

When receiving tunnel packets, if the hardware doesn't contain neighbor
information for the inner packet's destination IP, the entire encapsulated
packet is trapped to the CPU. In this case, we should ping the inner
destination IP to trigger the process of obtaining neighbor information
"""
import subprocess
import time
from datetime import datetime
from ipaddress import ip_interface

from swsscommon.swsscommon import ConfigDBConnector, SonicV2Connector
from sonic_py_common import logger as log

from pyroute2 import IPRoute
from scapy.layers.inet import IP
from scapy.layers.inet6 import IPv6
from scapy.sendrecv import AsyncSniffer


logger = log.Logger()

STATE_DB = 'STATE_DB'
PORTCHANNEL_INTERFACE_TABLE = 'PORTCHANNEL_INTERFACE'
TUNNEL_TABLE = 'TUNNEL'
PEER_SWITCH_TABLE = 'PEER_SWITCH'
INTF_TABLE_TEMPLATE = 'INTERFACE_TABLE|{}|{}'
STATE_KEY = 'state'
TUNNEL_TYPE_KEY = 'tunnel_type'
DST_IP_KEY = 'dst_ip'
ADDRESS_IPV4_KEY = 'address_ipv4'
IPINIP_TUNNEL = 'ipinip'

RTM_NEWLINK = 'RTM_NEWLINK'


class TunnelPacketHandler(object):
    """
    This class handles unroutable tunnel packets that are trapped
    to the CPU from the ASIC.
    """

    def __init__(self):
        self.config_db = ConfigDBConnector()
        self.config_db.connect()
        self.state_db = SonicV2Connector()
        self.state_db.connect(STATE_DB)
        self._portchannel_intfs = None
        self.up_portchannels = None
        self.netlink_api = IPRoute()
        self.sniffer = None
        self.self_ip = ''
        self.packet_filter = ''
        self.sniff_intfs = []

    @property
    def portchannel_intfs(self):
        """
        Gets all portchannel interfaces and IPv4 addresses in config DB

        Returns:
            (list) Tuples of a portchannel interface name (str) and
                   associated IPv4 address (str)
        """
        if self._portchannel_intfs is None:
            intf_keys = self.config_db.get_keys(PORTCHANNEL_INTERFACE_TABLE)
            portchannel_intfs = []

            for key in intf_keys:
                if isinstance(key, tuple) and len(key) > 1:
                    if ip_interface(key[1]).version == 4:
                        portchannel_intfs.append(key)

            self._portchannel_intfs = portchannel_intfs

        return self._portchannel_intfs

    def get_intf_name(self, msg):
        """
        Gets the interface name for a netlink msg

        Returns:
            (str) The interface name, or the empty string if no interface
                  name was found
        """
        attr_list = msg.get('attrs', list())

        for attribute, val in attr_list:
            if attribute == 'IFLA_IFNAME':
                return val

        return ''

    def netlink_msg_is_for_portchannel(self, msg):
        """
        Determines if a netlink message is about a PortChannel interface

        Returns:
            (list) integers representing kernel indices
        """
        ifname = self.get_intf_name(msg)

        return ifname in [name for name, _ in self.portchannel_intfs]

    def get_up_portchannels(self):
        """
        Returns the portchannels which are operationally up

        Returns:
            (list) of interface names which are up, as strings
        """
        portchannel_intf_names = [name for name, _ in self.portchannel_intfs]
        link_statuses = []
        for intf in portchannel_intf_names:
            status = self.netlink_api.link("get", ifname=intf)
            link_statuses.append(status[0])
        up_portchannels = []

        for status in link_statuses:
            if status['state'] == 'up':
                up_portchannels.append(self.get_intf_name(status))

        return up_portchannels

    def all_portchannels_established(self):
        """
        Checks if the portchannel interfaces are established

        Note that this status does not indicate operational state
        Returns:
            (bool) True, if all interfaces are established
                   False, otherwise
        """
        intfs = self.portchannel_intfs
        for intf in intfs:
            intf_table_name = INTF_TABLE_TEMPLATE.format(intf[0], intf[1])
            intf_state = self.state_db.get(
                                STATE_DB,
                                intf_table_name,
                                STATE_KEY
                        )

            if intf_state and intf_state.lower() != 'ok':
                return False

        return True

    def wait_for_portchannels(self, interval=5, timeout=60):
        """
        Continuosly checks if all portchannel host interfaces are established

        Args:
            interval: the interval (in seconds) at which to perform the check
            timeout: maximum allowed duration (in seconds) to wait for
                     interfaces to come up

        Raises:
            RuntimeError if the timeout duration is reached and interfaces are
                still not up
        """
        start = datetime.now()

        while (datetime.now() - start).seconds < timeout:
            if self.all_portchannels_established():
                logger.log_info("All portchannel intfs are established")
                return None
            logger.log_info("Not all portchannel intfs are established")
            time.sleep(interval)

        raise RuntimeError('Portchannel intfs were not established '
                           'within {}'.format(timeout))

    def get_ipinip_tunnel_addrs(self):
        """
        Get the IP addresses used for the IPinIP tunnel

        These should be the Loopback0 addresses for this device and the
        peer device

        Returns:
            ((str) self_loopback_ip, (str) peer_loopback_ip)
            or
            (None, None) If the tunnel type is not IPinIP
                         or
                         if an error is encountered. This most likely means
                         the host device is not a dual ToR device
        """
        try:
            peer_switch = self.config_db.get_keys(PEER_SWITCH_TABLE)[0]
            tunnel = self.config_db.get_keys(TUNNEL_TABLE)[0]
        except IndexError:
            logger.log_warning('PEER_SWITCH or TUNNEL table '
                               'not found in config DB')
            return None, None

        try:
            tunnel_table = self.config_db.get_entry(TUNNEL_TABLE, tunnel)
            tunnel_type = tunnel_table[TUNNEL_TYPE_KEY].lower()
            self_loopback_ip = tunnel_table[DST_IP_KEY]
            peer_loopback_ip = self.config_db.get_entry(
                                PEER_SWITCH_TABLE, peer_switch
                                )[ADDRESS_IPV4_KEY]
        except KeyError as error:
            logger.log_warning(
                'PEER_SWITCH or TUNNEL table missing data, '
                'could not find key {}'
                .format(error)
            )
            return None, None

        if tunnel_type == IPINIP_TUNNEL:
            return self_loopback_ip, peer_loopback_ip

        return None, None

    def get_inner_pkt_type(self, packet):
        """
        Get the type of an inner encapsulated packet

        Returns:
            (str)  'v4' if the inner packet is IPv4
            (str)  'v6' if the inner packet is IPv6
            (bool) False if `packet` is not an IPinIP packet
        """
        if packet.haslayer(IP):
            # Determine inner packet type based on IP protocol number
            # The outer packet type should always be IPv4
            if packet[IP].proto == 4:
                return IP
            elif packet[IP].proto == 41:
                return IPv6
        return False

    def wait_for_netlink_msgs(self):
        """
        Gathers any RTM_NEWLINK messages

        Returns:
            (list) containing any received messages
        """
        msgs = []
        with IPRoute() as ipr:
            ipr.bind()
            for msg in ipr.get():
                if msg['event'] == RTM_NEWLINK:
                    msgs.append(msg)

        return msgs

    def sniffer_restart_required(self, messages):
        """
        Determines if the packet sniffer needs to be restarted

        A restart is required if all of the following conditions are met:
            1. A netlink message of type RTM_NEWLINK is received
               (this is checked by `wait_for_netlink_msgs`)
            2. The interface index of the message corresponds to a portchannel
               interface
            3. The state of the interface in the message is 'up'
                    Here, we do not care about an interface going down since
                    the sniffer is able to continue sniffing on the other
                    interfaces. However, if an interface has gone down and
                    come back up, we need to restart the sniffer to be able
                    to sniff traffic on the interface that has come back up.
        """
        for msg in messages:
            if self.netlink_msg_is_for_portchannel(msg):
                if msg['state'] == 'up':
                    logger.log_info('{} came back up, sniffer restart required'
                                    .format(self.get_intf_name(msg)))
                    return True
        return False

    def start_sniffer(self):
        """
        Starts an AsyncSniffer and waits for it to inititalize fully
        """
        self.sniffer = AsyncSniffer(
            iface=self.sniff_intfs,
            filter=self.packet_filter,
            prn=self.ping_inner_dst,
            store=0
        )
        self.sniffer.start()

        while not hasattr(self.sniffer, 'stop_cb'):
            time.sleep(0.1)

    def ping_inner_dst(self, packet):
        """
        Pings the inner destination IP for an encapsulated packet

        Args:
            packet: The encapsulated packet received
        """
        inner_packet_type = self.get_inner_pkt_type(packet)
        if inner_packet_type and packet[IP].dst == self.self_ip:
            cmds = ['timeout', '0.2', 'ping', '-c1',
                    '-W1', '-i0', '-n', '-q']
            if inner_packet_type == IPv6:
                cmds.append('-6')
            dst_ip = packet[IP].payload[inner_packet_type].dst
            cmds.append(dst_ip)
            logger.log_info("Running command '{}'".format(' '.join(cmds)))
            subprocess.run(cmds, stdout=subprocess.DEVNULL)

    def listen_for_tunnel_pkts(self):
        """
        Listens for tunnel packets that are trapped to CPU

        These packets may be trapped if there is no neighbor info for the
        inner packet destination IP in the hardware.
        """
        self.self_ip, peer_ip = self.get_ipinip_tunnel_addrs()
        if self.self_ip is None or peer_ip is None:
            logger.log_notice('Could not get tunnel addresses from '
                              'config DB, exiting...')
            return None

        self.packet_filter = 'host {} and host {}'.format(self.self_ip, peer_ip)
        logger.log_notice('Starting tunnel packet handler for {}'
                          .format(self.packet_filter))

        self.sniff_intfs = self.get_up_portchannels()
        logger.log_info("Listening on interfaces {}".format(self.sniff_intfs))

        self.start_sniffer()
        while True:
            msgs = self.wait_for_netlink_msgs()
            if self.sniffer_restart_required(msgs):
                self.sniffer.stop()
                sniff_intfs = self.get_up_portchannels()
                logger.log_notice('Restarting tunnel packet handler on '
                                  'interfaces {}'.format(sniff_intfs))
                self.start_sniffer()

    def run(self):
        """
        Entry point for the TunnelPacketHandler class
        """
        self.wait_for_portchannels()
        self.listen_for_tunnel_pkts()


def main():
    logger.set_min_log_priority_info()
    handler = TunnelPacketHandler()
    handler.run()


if __name__ == "__main__":
    main()

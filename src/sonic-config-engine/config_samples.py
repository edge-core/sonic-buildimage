#!/usr/bin/env python
import os
import sys
from natsort import natsorted

def generate_t1_sample_config(data):
    data['DEVICE_METADATA']['localhost']['hostname'] = 'sonic'
    data['DEVICE_METADATA']['localhost']['type'] = 'LeafRouter'
    data['DEVICE_METADATA']['localhost']['bgp_asn'] = '65100'
    data['LOOPBACK_INTERFACE'] = {"Loopback0|10.1.0.1/32": {}}
    data['BGP_NEIGHBOR'] = {}
    data['DEVICE_NEIGHBOR'] = {}
    data['INTERFACE'] = {}
    port_count = 0
    total_port_amount = len(data['PORT'])
    for port in natsorted(data['PORT']):
        data['PORT'][port]['admin_status'] = 'up'
        data['PORT'][port]['mtu'] = '9100'
        local_addr = '10.0.{}.{}'.format(2 * port_count / 256, 2 * port_count % 256)
        peer_addr = '10.0.{}.{}'.format(2 * port_count / 256, 2 * port_count % 256 + 1)
        peer_name='ARISTA{0:02d}{1}'.format(1+port_count%(total_port_amount/2), 'T2' if port_count < (total_port_amount/2) else 'T0')
        peer_asn = 65200 if port_count < total_port_amount/2 else 64001 + port_count - total_port_amount/2
        data['INTERFACE']['{}|{}/31'.format(port, local_addr)] = {}
        data['BGP_NEIGHBOR'][peer_addr] = {
                'rrclient': 0,
                'name': peer_name,
                'local_addr': local_addr,
                'nhopself': 0,
                'holdtime': '180',
                'asn': str(peer_asn),
                'keepalive': '60'
                }
        port_count += 1
    return data;

def generate_empty_config(data):
    new_data = {'DEVICE_METADATA': data['DEVICE_METADATA']}
    if 'hostname' not in new_data['DEVICE_METADATA']['localhost']:
        new_data['DEVICE_METADATA']['localhost']['hostname'] = 'sonic'
    if 'type' not in new_data['DEVICE_METADATA']['localhost']:
        new_data['DEVICE_METADATA']['localhost']['type'] = 'LeafRouter'
    return new_data

def generate_l2_config(data):
    if 'hostname' not in data['DEVICE_METADATA']['localhost']:
        data['DEVICE_METADATA']['localhost']['hostname'] = 'sonic'
    if 'type' not in data['DEVICE_METADATA']['localhost']:
        data['DEVICE_METADATA']['localhost']['type'] = 'ToRRouter'
    data['VLAN'] = {'Vlan1000': {'vlanid': '1000'}}
    vp = natsorted(list(data['PORT'].keys()))
    data['VLAN']['Vlan1000'].setdefault('members', vp)
    data['VLAN_MEMBER'] = {}
    for port in natsorted(data['PORT']):
        data['PORT'][port].setdefault('admin_status', 'up')
        data['VLAN_MEMBER']['Vlan1000|{}'.format(port)] = {'tagging_mode': 'untagged'}
    return data

_sample_generators = {
        't1': generate_t1_sample_config,
        'l2': generate_l2_config,
        'empty': generate_empty_config
        }

def get_available_config():
    return list(_sample_generators.keys())

def generate_sample_config(data, setting_name):
    return _sample_generators[setting_name.lower()](data)


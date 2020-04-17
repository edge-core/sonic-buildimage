#!/usr/bin/env python
import os
import yaml
import subprocess
import re

DOCUMENTATION = '''
---
module: sonic_device_util
version_added: "1.9"
short_description: Retrieve device related facts for a device.
description:
    - Retrieve device related facts from config files.
'''

'''
TODO: this file shall be renamed and moved to other places in future
to have it shared with multiple applications. 
'''
def get_machine_info():
    if not os.path.isfile('/host/machine.conf'):
        return None
    machine_vars = {}
    with open('/host/machine.conf') as machine_file:
        for line in machine_file:
            tokens = line.split('=')
            if len(tokens) < 2:
                continue
            machine_vars[tokens[0]] = tokens[1].strip()
    return machine_vars

def get_platform_info(machine_info):
    if machine_info != None:
        if machine_info.has_key('onie_platform'):
            return  machine_info['onie_platform']
        elif machine_info.has_key('aboot_platform'):
            return machine_info['aboot_platform']
    return None

def get_sonic_version_info():
    if not os.path.isfile('/etc/sonic/sonic_version.yml'):
        return None
    data = {}
    with open('/etc/sonic/sonic_version.yml') as stream:
        if yaml.__version__ >= "5.1":
            data = yaml.full_load(stream)
        else:
            data = yaml.load(stream)
    return data

def valid_mac_address(mac):
    return bool(re.match("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", mac))

def get_system_mac():
    version_info = get_sonic_version_info()

    if (version_info['asic_type'] == 'mellanox'):
        # With Mellanox ONIE release(2019.05-5.2.0012) and above
        # "onie_base_mac" was added to /host/machine.conf:
        # onie_base_mac=e4:1d:2d:44:5e:80
        # So we have another way to get the mac address besides decode syseeprom
        # By this can mitigate the dependency on the hw-management service
        base_mac_key = "onie_base_mac"
        machine_vars = get_machine_info()
        if machine_vars is not None and base_mac_key in machine_vars:
            mac = machine_vars[base_mac_key]
            mac = mac.strip()
            if valid_mac_address(mac):
                return mac

        hw_mac_entry_cmds = [ "sudo decode-syseeprom -m" ]
    elif (version_info['asic_type'] == 'marvell'):
        # Try valid mac in eeprom, else fetch it from eth0
        platform = get_platform_info(get_machine_info())
        hwsku = get_machine_info()['onie_machine']
        profile_cmd = 'cat /usr/share/sonic/device/' + platform +'/'+ hwsku +'/profile.ini | cut -f2 -d='
        hw_mac_entry_cmds = [ profile_cmd, "sudo decode-syseeprom -m", "ip link show eth0 | grep ether | awk '{print $2}'" ]
    else:
        hw_mac_entry_cmds = [ "ip link show eth0 | grep ether | awk '{print $2}'" ]

    for get_mac_cmd in hw_mac_entry_cmds:
        proc = subprocess.Popen(get_mac_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (mac, err) = proc.communicate()
        if err:
            continue
        mac = mac.strip()
        if valid_mac_address(mac):
            break

    if not valid_mac_address(mac):
        return None

    # Align last byte of MAC if necessary
    if version_info and version_info['asic_type'] == 'centec':
        last_byte = mac[-2:]
        aligned_last_byte = format(int(int(last_byte, 16) + 1), '02x')
        mac = mac[:-2] + aligned_last_byte
    return mac

#
# Function to obtain the routing-stack being utilized. Function is not
# platform-specific; it's being placed in this file temporarily till a more
# suitable location is identified as part of upcoming refactoring efforts.
#
def get_system_routing_stack():
    command = "sudo docker ps | grep bgp | awk '{print$2}' | cut -d'-' -f3 | cut -d':' -f1"

    try:
        proc = subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                shell=True,
                                stderr=subprocess.STDOUT)
        stdout = proc.communicate()[0]
        proc.wait()
        result = stdout.rstrip('\n')

    except OSError, e:
        raise OSError("Cannot detect routing-stack")

    return result

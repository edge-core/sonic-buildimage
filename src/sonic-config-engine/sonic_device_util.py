#!/usr/bin/env python
import os
import yaml
import subprocess
import re
from natsort import natsorted
import glob
from swsssdk import ConfigDBConnector, SonicDBConfig

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
SONIC_DEVICE_PATH = '/usr/share/sonic/device'
NPU_NAME_PREFIX = 'asic'
NAMESPACE_PATH_GLOB = '/run/netns/*'
ASIC_CONF_FILENAME = 'asic.conf'
FRONTEND_ASIC_SUB_ROLE = 'FrontEnd'
BACKEND_ASIC_SUB_ROLE = 'BackEnd'
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

def get_npu_id_from_name(npu_name):
    if npu_name.startswith(NPU_NAME_PREFIX):
        return npu_name[len(NPU_NAME_PREFIX):]
    else:
        return None

def get_asic_conf_file_path(platform):
    asic_conf_path_candidates = []
    asic_conf_path_candidates.append(os.path.join('/usr/share/sonic/platform', ASIC_CONF_FILENAME))
    if platform is not None:
        asic_conf_path_candidates.append(os.path.join(SONIC_DEVICE_PATH, platform, ASIC_CONF_FILENAME))
    for asic_conf_file_path in asic_conf_path_candidates:
        if os.path.isfile(asic_conf_file_path):
            return asic_conf_file_path
    return None

def get_num_npus():
    platform = get_platform_info(get_machine_info())
    asic_conf_file_path = get_asic_conf_file_path(platform)
    if asic_conf_file_path is None:
        return 1
    with open(asic_conf_file_path) as asic_conf_file:
        for line in asic_conf_file:
            tokens = line.split('=')
            if len(tokens) < 2:
               continue
            if tokens[0].lower() == 'num_asic':
                num_npus = tokens[1].strip()
        return int(num_npus)

def get_namespaces():
    """
    In a multi NPU platform, each NPU is in a Linux Namespace.
    This method returns list of all the Namespace present on the device
    """
    ns_list = []
    for path in glob.glob(NAMESPACE_PATH_GLOB):
        ns = os.path.basename(path)
        ns_list.append(ns)
    return natsorted(ns_list)

def get_hwsku():
    config_db = ConfigDBConnector()
    config_db.connect()
    metadata = config_db.get_table('DEVICE_METADATA')
    return metadata['localhost']['hwsku']

def get_platform():
    if not os.path.isfile('/host/machine.conf'):
        return ''
 
    with open('/host/machine.conf') as machine_conf:
        for line in machine_conf:
            tokens = line.split('=')
            if tokens[0].strip() == 'onie_platform' or tokens[0].strip() == 'aboot_platform':
                return tokens[1].strip()
    return ''

def is_multi_npu():
    num_npus = get_num_npus()
    return (num_npus > 1)

def get_all_namespaces():
    """
    In case of Multi-Asic platform, Each ASIC will have a linux network namespace created.
    So we loop through the databases in different namespaces and depending on the sub_role
    decide whether this is a front end ASIC/namespace or a back end one.
    """
    front_ns = []
    back_ns = []
    num_npus = get_num_npus()
    SonicDBConfig.load_sonic_global_db_config()
    
    if is_multi_npu():
        for npu in range(num_npus):
            namespace = "{}{}".format(NPU_NAME_PREFIX, npu)
            config_db = ConfigDBConnector(use_unix_socket_path=True, namespace=namespace)
            config_db.connect()

            metadata = config_db.get_table('DEVICE_METADATA')
            if metadata['localhost']['sub_role'] == FRONTEND_ASIC_SUB_ROLE:
                front_ns.append(namespace)
            elif metadata['localhost']['sub_role'] == BACKEND_ASIC_SUB_ROLE:
                back_ns.append(namespace)

    return {'front_ns':front_ns, 'back_ns':back_ns}

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

def get_system_mac(namespace=None):
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
        profile_cmd = 'cat' + SONIC_DEVICE_PATH + '/' + platform +'/'+ hwsku +'/profile.ini | grep switchMacAddress | cut -f2 -d='
        hw_mac_entry_cmds = [ profile_cmd, "sudo decode-syseeprom -m", "ip link show eth0 | grep ether | awk '{print $2}'" ]
    else:
        mac_address_cmd = "cat /sys/class/net/eth0/address"
        if namespace is not None:
            mac_address_cmd = "sudo ip netns exec {} {}".format(namespace, mac_address_cmd)
       
        hw_mac_entry_cmds = [mac_address_cmd]

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

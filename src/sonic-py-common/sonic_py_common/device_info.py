import glob
import json
import os
import re
import subprocess

import yaml
from natsort import natsorted

# TODO: Replace with swsscommon
from swsssdk import ConfigDBConnector, SonicDBConfig, SonicV2Connector

USR_SHARE_SONIC_PATH = "/usr/share/sonic"
HOST_DEVICE_PATH = USR_SHARE_SONIC_PATH + "/device"
CONTAINER_PLATFORM_PATH = USR_SHARE_SONIC_PATH + "/platform"

MACHINE_CONF_PATH = "/host/machine.conf"
SONIC_VERSION_YAML_PATH = "/etc/sonic/sonic_version.yml"

# Port configuration file names
PORT_CONFIG_FILE = "port_config.ini"
PLATFORM_JSON_FILE = "platform.json"

# HwSKU configuration file name
HWSKU_JSON_FILE = 'hwsku.json'

# Multi-NPU constants
# TODO: Move Multi-ASIC-related functions and constants to a "multi_asic.py" module
NPU_NAME_PREFIX = "asic"
NAMESPACE_PATH_GLOB = "/run/netns/*"
ASIC_CONF_FILENAME = "asic.conf"
FRONTEND_ASIC_SUB_ROLE = "FrontEnd"
BACKEND_ASIC_SUB_ROLE = "BackEnd"


def get_localhost_info(field):
    try:
        config_db = ConfigDBConnector()
        config_db.connect()

        metadata = config_db.get_table('DEVICE_METADATA')

        if 'localhost' in metadata and field in metadata['localhost']:
            return metadata['localhost'][field]
    except Exception:
        pass

    return None


def get_hostname():
    return get_localhost_info('hostname')


def get_machine_info():
    """
    Retreives data from the machine configuration file

    Returns:
        A dictionary containing the key/value pairs as found in the machine
        configuration file
    """
    if not os.path.isfile(MACHINE_CONF_PATH):
        return None

    machine_vars = {}
    with open(MACHINE_CONF_PATH) as machine_conf_file:
        for line in machine_conf_file:
            tokens = line.split('=')
            if len(tokens) < 2:
                continue
            machine_vars[tokens[0]] = tokens[1].strip()

    return machine_vars


def get_platform():
    """
    Retrieve the device's platform identifier

    Returns:
        A string containing the device's platform identifier
    """

    # If we are running in a virtual switch Docker container, the environment
    # variable 'PLATFORM' will be defined and will contain the platform
    # identifier.
    platform_env = os.getenv("PLATFORM")
    if platform_env:
        return platform_env

    # If 'PLATFORM' env variable is not defined, we try to read the platform
    # identifier from machine.conf. This is critical for sonic-config-engine,
    # because it is responsible for populating this value in Config DB.
    machine_info = get_machine_info()
    if machine_info:
        if 'onie_platform' in machine_info:
            return machine_info['onie_platform']
        elif 'aboot_platform' in machine_info:
            return machine_info['aboot_platform']

    # If we fail to read from machine.conf, we may be running inside a Docker
    # container in SONiC, where the /host directory is not mounted. In this
    # case the value should already be populated in Config DB so we finally
    # try reading it from there.
    
    return get_localhost_info('platform')


def get_hwsku():
    """
    Retrieve the device's hardware SKU identifier

    Returns:
        A string containing the device's hardware SKU identifier
    """

    return get_localhost_info('hwsku')


def get_platform_and_hwsku():
    """
    Convenience function which retrieves both the device's platform identifier
    and hardware SKU identifier

    Returns:
        A tuple of two strings, the first containing the device's
        platform identifier, the second containing the device's
        hardware SKU identifier
    """
    platform = get_platform()
    hwsku = get_hwsku()

    return (platform, hwsku)


def get_asic_conf_file_path():
    """
    Retrieves the path to the ASIC conguration file on the device

    Returns:
        A string containing the path to the ASIC conguration file on success,
        None on failure
    """
    asic_conf_path_candidates = []

    asic_conf_path_candidates.append(os.path.join(CONTAINER_PLATFORM_PATH, ASIC_CONF_FILENAME))

    platform = get_platform()
    if platform:
        asic_conf_path_candidates.append(os.path.join(HOST_DEVICE_PATH, platform, ASIC_CONF_FILENAME))

    for asic_conf_file_path in asic_conf_path_candidates:
        if os.path.isfile(asic_conf_file_path):
            return asic_conf_file_path

    return None


def get_path_to_platform_dir():
    """
    Retreives the paths to the device's platform directory

    Returns:
        A string containing the path to the platform directory of the device
    """
    # Get platform
    platform = get_platform()

    # Determine whether we're running in a container or on the host
    platform_path_host = os.path.join(HOST_DEVICE_PATH, platform)

    if os.path.isdir(CONTAINER_PLATFORM_PATH):
        platform_path = CONTAINER_PLATFORM_PATH
    elif os.path.isdir(platform_path_host):
        platform_path = platform_path_host
    else:
        raise OSError("Failed to locate platform directory")

    return platform_path

def get_path_to_hwsku_dir():
    """
    Retreives the path to the device's hardware SKU data directory

    Returns:
        A string, containing the path to the hardware SKU directory of the device
    """

    # Get Platform path first
    platform_path = get_path_to_platform_dir()

    # Get hwsku
    hwsku = get_hwsku()

    hwsku_path = os.path.join(platform_path, hwsku)

    return hwsku_path

def get_paths_to_platform_and_hwsku_dirs():
    """
    Retreives the paths to the device's platform and hardware SKU data
    directories

    Returns:
        A tuple of two strings, the first containing the path to the platform
        directory of the device, the second containing the path to the hardware
        SKU directory of the device
    """

    # Get Platform path first
    platform_path = get_path_to_platform_dir()

    # Get hwsku
    hwsku = get_hwsku()

    hwsku_path = os.path.join(platform_path, hwsku)

    return (platform_path, hwsku_path)

def get_path_to_port_config_file(hwsku=None, asic=None):
    """
    Retrieves the path to the device's port configuration file

    Args:
        hwsku: a string, it is allowed to be passed in args because when loading the
              initial configuration on the device, the HwSKU is not yet present in ConfigDB.
        asic: a string , asic argument should be passed on multi-ASIC devices only,
              it should be omitted on single-ASIC platforms.

    Returns:
        A string containing the path the the device's port configuration file
    """

    """
    This platform check is performed to make sure we return a None
    in case of unit-tests within sonic-cfggen where platform is not expected to be
    present because tests are not run on actual Hardware/Container.
    TODO: refactor sonic-cfggen such that we can remove this check
    """

    platform = get_platform()
    if not platform:
        return None

    if hwsku:
        platform_path = get_path_to_platform_dir()
        hwsku_path = os.path.join(platform_path, hwsku)
    else:
        (platform_path, hwsku_path) = get_paths_to_platform_and_hwsku_dirs()

    port_config_candidates = []

    # Check for 'hwsku.json' file presence first
    hwsku_json_file = os.path.join(hwsku_path, HWSKU_JSON_FILE)

    # if 'hwsku.json' file is available, Check for 'platform.json' file presence,
    # if 'platform.json' is available, APPEND it. Otherwise, SKIP it.

    """
    This length check for interfaces in platform.json is performed to make sure
    the cfggen does not fail if port configuration information is not present
    TODO: once platform.json has all the necessary port config information
          remove this check
    """

    if os.path.isfile(hwsku_json_file):
        if os.path.isfile(os.path.join(platform_path, PLATFORM_JSON_FILE)):
            json_file = os.path.join(platform_path, PLATFORM_JSON_FILE)
            platform_data = json.loads(open(json_file).read())
            interfaces = platform_data.get('interfaces', None)
            if interfaces is not None and len(interfaces) > 0:
                port_config_candidates.append(os.path.join(platform_path, PLATFORM_JSON_FILE))

    # Check for 'port_config.ini' file presence in a few locations
    if asic:
        port_config_candidates.append(os.path.join(hwsku_path, asic, PORT_CONFIG_FILE))
    else:
        port_config_candidates.append(os.path.join(hwsku_path, PORT_CONFIG_FILE))

    for candidate in port_config_candidates:
        if os.path.isfile(candidate):
            return candidate

    return None

def get_sonic_version_info():
    if not os.path.isfile(SONIC_VERSION_YAML_PATH):
        return None

    data = {}
    with open(SONIC_VERSION_YAML_PATH) as stream:
        if yaml.__version__ >= "5.1":
            data = yaml.full_load(stream)
        else:
            data = yaml.load(stream)

    return data

def get_sonic_version_file():
    if not os.path.isfile(SONIC_VERSION_YAML_PATH):
        return None

    return SONIC_VERSION_YAML_PATH

#
# Multi-NPU functionality
#

def get_num_npus():
    asic_conf_file_path = get_asic_conf_file_path()
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


def is_multi_npu():
    num_npus = get_num_npus()
    return (num_npus > 1)


def get_npu_id_from_name(npu_name):
    if npu_name.startswith(NPU_NAME_PREFIX):
        return npu_name[len(NPU_NAME_PREFIX):]
    else:
        return None


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


def _valid_mac_address(mac):
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
            if _valid_mac_address(mac):
                return mac

        hw_mac_entry_cmds = [ "sudo decode-syseeprom -m" ]
    elif (version_info['asic_type'] == 'marvell'):
        # Try valid mac in eeprom, else fetch it from eth0
        platform = get_platform()
        machine_key = "onie_machine"
        machine_vars = get_machine_info()
        if machine_vars is not None and machine_key in machine_vars:
            hwsku = machine_vars[machine_key]
            profile_cmd = 'cat ' + HOST_DEVICE_PATH + '/' + platform + '/' + hwsku + '/profile.ini | grep switchMacAddress | cut -f2 -d='
        else:
            profile_cmd = "false"
        hw_mac_entry_cmds = ["sudo decode-syseeprom -m", profile_cmd, "ip link show eth0 | grep ether | awk '{print $2}'"]
    else:
        mac_address_cmd = "cat /sys/class/net/eth0/address"
        if namespace is not None:
            mac_address_cmd = "sudo ip netns exec {} {}".format(namespace, mac_address_cmd)

        hw_mac_entry_cmds = [mac_address_cmd]

    for get_mac_cmd in hw_mac_entry_cmds:
        proc = subprocess.Popen(get_mac_cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (mac, err) = proc.communicate()
        if err:
            continue
        mac = mac.strip()
        if _valid_mac_address(mac):
            break

    if not _valid_mac_address(mac):
        return None

    # Align last byte of MAC if necessary
    if version_info and version_info['asic_type'] == 'centec':
        last_byte = mac[-2:]
        aligned_last_byte = format(int(int(last_byte, 16) + 1), '02x')
        mac = mac[:-2] + aligned_last_byte
    return mac


def get_system_routing_stack():
    """
    Retrieves the routing stack being utilized on this device

    Returns:
        A string containing the name of the routing stack in use on the device
    """
    command = "sudo docker ps | grep bgp | awk '{print$2}' | cut -d'-' -f3 | cut -d':' -f1"

    try:
        proc = subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                shell=True,
                                universal_newlines=True,
                                stderr=subprocess.STDOUT)
        stdout = proc.communicate()[0]
        proc.wait()
        result = stdout.rstrip('\n')
    except OSError as e:
        raise OSError("Cannot detect routing stack")

    return result

# Check if System warm reboot or Container warm restart is enabled.
def is_warm_restart_enabled(container_name):
    state_db = SonicV2Connector(host='127.0.0.1')
    state_db.connect(state_db.STATE_DB, False)

    TABLE_NAME_SEPARATOR = '|'
    prefix = 'WARM_RESTART_ENABLE_TABLE' + TABLE_NAME_SEPARATOR

    # Get the system warm reboot enable state
    _hash = '{}{}'.format(prefix, 'system')
    wr_system_state = state_db.get(state_db.STATE_DB, _hash, "enable")
    wr_enable_state = True if wr_system_state == "true" else False

    # Get the container warm reboot enable state
    _hash = '{}{}'.format(prefix, container_name)
    wr_container_state = state_db.get(state_db.STATE_DB, _hash, "enable")
    wr_enable_state |= True if wr_container_state == "true" else False

    state_db.close(state_db.STATE_DB)
    return wr_enable_state

# Check if System fast reboot is enabled.
def is_fast_reboot_enabled():
    fb_system_state = 0
    cmd = 'sonic-db-cli STATE_DB get "FAST_REBOOT|system"'
    proc = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE)
    (stdout, stderr) = proc.communicate()

    if proc.returncode != 0:
        log.log_error("Error running command '{}'".format(cmd))
    elif stdout:
        fb_system_state = stdout.rstrip('\n')

    return fb_system_state

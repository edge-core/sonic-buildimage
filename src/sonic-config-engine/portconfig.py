#!/usr/bin/env python
try:
    import os
    import sys
    import json
    import ast
    import re
    from collections import OrderedDict
    from swsssdk import ConfigDBConnector
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))

# Global Variable
PLATFORM_ROOT_PATH = '/usr/share/sonic/device'
PLATFORM_ROOT_PATH_DOCKER = '/usr/share/sonic/platform'
SONIC_ROOT_PATH = '/usr/share/sonic'
HWSKU_ROOT_PATH = '/usr/share/sonic/hwsku'

PLATFORM_JSON = 'platform.json'
PORT_CONFIG_INI = 'port_config.ini'
HWSKU_JSON = 'hwsku.json'

PORT_STR = "Ethernet"
BRKOUT_MODE = "default_brkout_mode"
CUR_BRKOUT_MODE = "brkout_mode"
INTF_KEY = "interfaces"

BRKOUT_PATTERN = r'(\d{1,3})x(\d{1,3}G)(\[\d{1,3}G\])?(\((\d{1,3})\))?'


#
# Helper Functions
#
def readJson(filename):
    # Read 'platform.json' or 'hwsku.json' file
    try:
        with open(filename) as fp:
            try:
                data = json.load(fp)
            except json.JSONDecodeError:
                print("Json file does not exist")
        data_dict = ast.literal_eval(json.dumps(data))
        return data_dict
    except Exception as e:
        print("error occurred while parsing json: {}".format(sys.exc_info()[1]))
        return None

def db_connect_configdb():
    """
    Connect to configdb
    """
    config_db = ConfigDBConnector()
    if config_db is None:
        return None
    try:
        """
        This could be blocking during the config load_minigraph phase,
        as the CONFIG_DB_INITIALIZED is not yet set in the configDB.
        We can ignore the check by using config_db.db_connect('CONFIG_DB') instead
        """
        # Connect only if available & initialized
        config_db.connect(wait_for_init=False)
    except Exception as e:
        config_db = None
    return config_db

def get_port_config_file_name(hwsku=None, platform=None, asic=None):

    # check 'platform.json' file presence
    port_config_candidates_Json = []
    port_config_candidates_Json.append(os.path.join(PLATFORM_ROOT_PATH_DOCKER, PLATFORM_JSON))
    if platform:
        port_config_candidates_Json.append(os.path.join(PLATFORM_ROOT_PATH, platform, PLATFORM_JSON))

    # check 'portconfig.ini' file presence
    port_config_candidates = []
    port_config_candidates.append(os.path.join(HWSKU_ROOT_PATH, PORT_CONFIG_INI))
    if hwsku:
        if platform:
            if asic:
                port_config_candidates.append(os.path.join(PLATFORM_ROOT_PATH, platform, hwsku, asic, PORT_CONFIG_INI))
            port_config_candidates.append(os.path.join(PLATFORM_ROOT_PATH, platform, hwsku, PORT_CONFIG_INI))
        port_config_candidates.append(os.path.join(PLATFORM_ROOT_PATH_DOCKER, hwsku, PORT_CONFIG_INI))
        port_config_candidates.append(os.path.join(SONIC_ROOT_PATH, hwsku, PORT_CONFIG_INI))

    elif platform and not hwsku:
        port_config_candidates.append(os.path.join(PLATFORM_ROOT_PATH, platform, PORT_CONFIG_INI))

    for candidate in port_config_candidates_Json + port_config_candidates:
        if os.path.isfile(candidate):
            return candidate
    return None

def get_hwsku_file_name(hwsku=None, platform=None):
    hwsku_candidates_Json = []
    hwsku_candidates_Json.append(os.path.join(HWSKU_ROOT_PATH, HWSKU_JSON))
    if hwsku:
        if platform:
            hwsku_candidates_Json.append(os.path.join(PLATFORM_ROOT_PATH, platform, hwsku, HWSKU_JSON))
        hwsku_candidates_Json.append(os.path.join(PLATFORM_ROOT_PATH_DOCKER, hwsku, HWSKU_JSON))
        hwsku_candidates_Json.append(os.path.join(SONIC_ROOT_PATH, hwsku, HWSKU_JSON))
    for candidate in hwsku_candidates_Json:
        if os.path.isfile(candidate):
            return candidate
    return None

def get_port_config(hwsku=None, platform=None, port_config_file=None, hwsku_config_file=None, asic=None):
    config_db = db_connect_configdb()
    # If available, Read from CONFIG DB first
    if config_db is not None and port_config_file is None:

        port_data = config_db.get_table("PORT")
        if bool(port_data):
            ports = ast.literal_eval(json.dumps(port_data))
            port_alias_map = {}
            port_alias_asic_map = {}
            for intf_name in ports.keys():
                port_alias_map[ports[intf_name]["alias"]] = intf_name
            return (ports, port_alias_map, port_alias_asic_map)

    if not port_config_file:
        port_config_file = get_port_config_file_name(hwsku, platform, asic)
        if not port_config_file:
            return ({}, {}, {})


    # Read from 'platform.json' file
    if port_config_file.endswith('.json'):
        if not hwsku_config_file:
             hwsku_json_file = get_hwsku_file_name(hwsku, platform)
             if not hwsku_json_file:
                return ({}, {}, {})
        else:
            hwsku_json_file = hwsku_config_file

        return parse_platform_json_file(hwsku_json_file, port_config_file)

    # If 'platform.json' file is not available, read from 'port_config.ini'
    else:
        return parse_port_config_file(port_config_file)

def parse_port_config_file(port_config_file):
    ports = {}
    port_alias_map = {}
    port_alias_asic_map = {}
    # Default column definition
    titles = ['name', 'lanes', 'alias', 'index']
    with open(port_config_file) as data:
        for line in data:
            if line.startswith('#'):
                if "name" in line:
                    titles = line.strip('#').split()
                continue;
            tokens = line.split()
            if len(tokens) < 2:
                continue
            name_index = titles.index('name')
            name = tokens[name_index]
            data = {}
            for i, item in enumerate(tokens):
                if i == name_index:
                    continue
                data[titles[i]] = item
            data.setdefault('alias', name)
            ports[name] = data
            port_alias_map[data['alias']] = name
            # asic_port_name to sonic_name mapping also included in
            # port_alias_map
            if (('asic_port_name' in data) and
                (data['asic_port_name'] != name)):
                port_alias_map[data['asic_port_name']] = name
            # alias to asic_port_name mapping
            if 'asic_port_name' in data:
                port_alias_asic_map[data['alias']] = data['asic_port_name'].strip()
    return (ports, port_alias_map, port_alias_asic_map)

# Generate configs (i.e. alias, lanes, speed, index) for port
def gen_port_config(ports, parent_intf_id, index, alias_at_lanes, lanes, k,  offset):
    if k is not None:
        num_lane_used, speed, alt_speed, _ , assigned_lane = k[0], k[1], k[2], k[3], k[4]

        # In case of symmetric mode
        if assigned_lane is None:
            assigned_lane = len(lanes.split(","))

        parent_intf_id = int(offset)+int(parent_intf_id)
        alias_start = 0 + offset

        step = int(assigned_lane)//int(num_lane_used)
        for i in range(0,int(assigned_lane), step):
            intf_name = PORT_STR + str(parent_intf_id)
            ports[intf_name] = {}
            ports[intf_name]['alias'] = alias_at_lanes.split(",")[alias_start]
            ports[intf_name]['lanes'] = ','.join(lanes.split(",")[alias_start:alias_start+step])
            if speed:
                speed_pat = re.search("^((\d+)G|\d+)$", speed.upper())
                if speed_pat is None:
                    raise Exception('{} speed is not Supported...'.format(speed))
                speed_G, speed_orig = speed_pat.group(2), speed_pat.group(1)
                if speed_G:
                    conv_speed = int(speed_G)*1000
                else:
                    conv_speed = int(speed_orig)
                ports[intf_name]['speed'] = str(conv_speed)
            else:
                raise Exception('Regex return for speed is None...')

            ports[intf_name]['index'] = index.split(",")[alias_start]
            ports[intf_name]['admin_status'] = "up"

            parent_intf_id += step
            alias_start += step

        offset = int(assigned_lane) + int(offset)
        return offset
    else:
        raise Exception('Regex return for k is None...')

"""
Given a port and breakout mode, this method returns
the list of child ports using platform_json file
"""
def get_child_ports(interface, breakout_mode, platform_json_file):
    child_ports = {}

    port_dict = readJson(platform_json_file)

    index = port_dict[INTF_KEY][interface]['index']
    alias_at_lanes = port_dict[INTF_KEY][interface]['alias_at_lanes']
    lanes = port_dict[INTF_KEY][interface]['lanes']

    """
    Example of match_list for some breakout_mode using regex
        Breakout Mode -------> Match_list
        -----------------------------
        2x25G(2)+1x50G(2) ---> [('2', '25G', None, '(2)', '2'), ('1', '50G', None, '(2)', '2')]
        1x50G(2)+2x25G(2) ---> [('1', '50G', None, '(2)', '2'), ('2', '25G', None, '(2)', '2')]
        1x100G[40G] ---------> [('1', '100G', '[40G]', None, None)]
        2x50G ---------------> [('2', '50G', None, None, None)]
    """
    # Asymmetric breakout mode
    if re.search("\+",breakout_mode) is not None:
        breakout_parts = breakout_mode.split("+")
        match_list = [re.match(BRKOUT_PATTERN, i).groups() for i in breakout_parts]

    # Symmetric breakout mode
    else:
        match_list = [re.match(BRKOUT_PATTERN, breakout_mode).groups()]

    offset = 0
    parent_intf_id = int(re.search("Ethernet(\d+)", interface).group(1))
    for k in match_list:
        offset = gen_port_config(child_ports, parent_intf_id, index, alias_at_lanes, lanes, k, offset)
    return child_ports

def parse_platform_json_file(hwsku_json_file, platform_json_file):
    ports = {}
    port_alias_map = {}
    port_alias_asic_map = {}

    port_dict = readJson(platform_json_file)
    hwsku_dict = readJson(hwsku_json_file)

    if not port_dict:
        raise Exception("port_dict is none")
    if not hwsku_dict:
        raise Exception("hwsku_dict is none")

    if INTF_KEY not in port_dict or INTF_KEY not in  hwsku_dict:
        raise Exception("INTF_KEY is not present in appropriate file")

    for intf in port_dict[INTF_KEY]:
        if intf not in hwsku_dict[INTF_KEY]:
            raise Exception("{} is not available in hwsku_dict".format(intf))

        # take default_brkout_mode from hwsku.json
        brkout_mode = hwsku_dict[INTF_KEY][intf][BRKOUT_MODE]

        child_ports = get_child_ports(intf, brkout_mode, platform_json_file)
        ports.update(child_ports)

    if not ports:
        raise Exception("Ports dictionary is empty")

    for i in ports.keys():
        port_alias_map[ports[i]["alias"]]= i
    return (ports, port_alias_map, port_alias_asic_map)


def get_breakout_mode(hwsku=None, platform=None, port_config_file=None):
    if not port_config_file:
        port_config_file = get_port_config_file_name(hwsku, platform)
        if not port_config_file:
            return None
    if port_config_file.endswith('.json'):
        hwsku_json_file = get_hwsku_file_name(hwsku, platform)
        if not hwsku_json_file:
            raise Exception("'hwsku_json' file does not exist!!! This file is necessary to proceed forward.")

        return parse_breakout_mode(hwsku_json_file)
    else:
        return None

def parse_breakout_mode(hwsku_json_file):
    brkout_table = {}
    hwsku_dict = readJson(hwsku_json_file)
    if not hwsku_dict:
        raise Exception("hwsku_dict is empty")
    if INTF_KEY not in  hwsku_dict:
        raise Exception("INTF_KEY is not present in hwsku_dict")

    for intf in hwsku_dict[INTF_KEY]:
        brkout_table[intf] = {}
        brkout_table[intf][CUR_BRKOUT_MODE] = hwsku_dict[INTF_KEY][intf][BRKOUT_MODE]
    return brkout_table

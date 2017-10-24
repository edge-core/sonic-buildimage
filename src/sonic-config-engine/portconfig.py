#!/usr/bin/env python
import os
import sys


def get_port_config_file_name(hwsku=None, platform=None):
    port_config_candidates = []
    port_config_candidates.append('/usr/share/sonic/hwsku/port_config.ini')
    if hwsku:
        if platform:
            port_config_candidates.append(os.path.join('/usr/share/sonic/device', platform, hwsku, 'port_config.ini'))
        port_config_candidates.append(os.path.join('/usr/share/sonic/platform', hwsku, 'port_config.ini'))
        port_config_candidates.append(os.path.join('/usr/share/sonic', hwsku, 'port_config.ini'))
    for candidate in port_config_candidates:
        if os.path.isfile(candidate):
            return candidate
    return None
    

def get_port_config(hwsku=None, platform=None, port_config_file=None):
    if not port_config_file:
        port_config_file = get_port_config_file_name(hwsku, platform)
        if not port_config_file:
            return ({}, {})
    return parse_port_config_file(port_config_file)


def parse_port_config_file(port_config_file):
    ports = {}
    port_alias_map = {}
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
    return (ports, port_alias_map)



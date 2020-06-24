#!/usr/bin/env python3

import json
import subprocess

INIT_CFG_FILE_PATH = '/etc/sonic/init_cfg.json'

with open(INIT_CFG_FILE_PATH) as init_cfg_file:
    init_cfg = json.load(init_cfg_file)
    if 'FEATURE' in init_cfg:
        for feature_name, feature_props in init_cfg['FEATURE'].items():
            if 'status' in feature_props and feature_props['status'] == 'disabled':
                subprocess.run(['systemctl', 'mask', '{}.service'.format(feature_name)])

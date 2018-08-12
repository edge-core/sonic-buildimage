#!/usr/bin/env python

import sys, errno
import time
import os
from python_sdk_api.sxd_api import *
from python_sdk_api.sx_api import *

def get_log_ports(handle, sfp_module):
    port_attributes_list = new_sx_port_attributes_t_arr(64)
    port_cnt_p = new_uint32_t_p()
    uint32_t_p_assign(port_cnt_p, 64)

    rc = sx_api_port_device_get(handle, 1 , 0, port_attributes_list,  port_cnt_p)
    assert rc == SX_STATUS_SUCCESS, "sx_api_port_device_get failed, rc = %d" % rc

    port_cnt = uint32_t_p_value(port_cnt_p)
    log_port_list = []
    for i in range(0, port_cnt):
        port_attributes = sx_port_attributes_t_arr_getitem(port_attributes_list, i)
        if port_attributes.port_mapping.module_port == sfp_module:
            log_port_list.append(port_attributes.log_port)

    return log_port_list

def set_sfp_admin_status(handle, meta, sfp_module, sfp_log_port_list, admin_status):
    # Get PMAOS
    pmaos = ku_pmaos_reg()
    pmaos.module = sfp_module
    meta.access_cmd = SXD_ACCESS_CMD_GET
    rc = sxd_access_reg_pmaos(pmaos, meta, 1, None, None)
    assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_pmaos failed, rc = %d" % rc

    # Set admin status to PMAOS
    pmaos.ase = 1
    pmaos.ee = 1
    pmaos.e = 2
    pmaos.rst = 0
    if admin_status == SX_PORT_ADMIN_STATUS_DOWN:
        pmaos.admin_status = 2
    else:
        pmaos.admin_status = 1

    meta.access_cmd = SXD_ACCESS_CMD_SET
    rc = sxd_access_reg_pmaos(pmaos, meta, 1, None, None)
    assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_pmaos failed, rc = %d" % rc

# Check if SFP port number is provided
if len(sys.argv) < 3:
    print "SFP module number or LPM is missed."
    print "Usage: sfplpmset.py <SFP module> <on|off>"
    sys.exit(errno.EINVAL)

lpm_enable = None
if sys.argv[2] == 'on':
    lpm_enable = True
elif sys.argv[2] == 'off':
    lpm_enable = False
else:
    print "Unrecognized LPM parameter. Please use <on> or <off> values"
    sys.exit(errno.EINVAL)

# Init SDK API
rc, handle = sx_api_open(None)
if (rc != SX_STATUS_SUCCESS):
    print "Failed to open api handle.\nPlease check that SDK is running."
    sys.exit(errno.EACCES)

pid = os.getpid()
rc = sxd_access_reg_init(pid, None, 0)
if (rc != 0):
    print "Failed to initializing register access.\nPlease check that SDK is running."
    sys.exit(errno.EACCES);

# Get SFP module and log ports number and LPM status
sfp_module = int(sys.argv[1])
log_port_list = get_log_ports(handle, sfp_module)
if not log_port_list:
    print "Failed to get log ports"
    sys.exit(errno.EACCES)

# Get PMMP
pmmp = ku_pmmp_reg()
pmmp.module = sfp_module
meta = sxd_reg_meta_t()
meta.dev_id = 1
meta.swid = 0
meta.access_cmd = SXD_ACCESS_CMD_GET
rc = sxd_access_reg_pmmp(pmmp, meta, 1, None, None)
assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_pmmp failed, rc = %d" % rc

# Disable admin status before LPM settings
set_sfp_admin_status(handle, meta, sfp_module, log_port_list, SX_PORT_ADMIN_STATUS_DOWN)

# Set low power mode status
lpm_mask = 1 << 8
if lpm_enable:
    pmmp.eeprom_override = pmmp.eeprom_override | lpm_mask
else:
    pmmp.eeprom_override = pmmp.eeprom_override & (~lpm_mask)

meta.access_cmd = SXD_ACCESS_CMD_SET
rc = sxd_access_reg_pmmp(pmmp, meta, 1, None, None)
assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_pmmp failed, rc = %d" % rc

# Enable admin status after LPM settings
set_sfp_admin_status(handle, meta, sfp_module, log_port_list, SX_PORT_ADMIN_STATUS_UP)

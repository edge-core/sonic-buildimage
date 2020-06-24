#!/usr/bin/env python

import sys, errno
import os
from python_sdk_api.sxd_api import *
from python_sdk_api.sx_api import *

REGISTER_NUM = 1
SXD_LOG_VERBOSITY_LEVEL = 0
DEVICE_ID = 1
SWITCH_ID = 0
SX_PORT_ATTR_ARR_SIZE = 64

PMAOS_ASE = 1
PMAOS_EE = 1
PMAOS_E = 2
PMAOS_RST = 0
PMAOS_ENABLE = 1
PMAOS_DISABLE = 2

PORT_TYPE_CPU = 4
PORT_TYPE_NVE = 8
PORT_TYPE_OFFSET = 28
PORT_TYPE_MASK = 0xF0000000
NVE_MASK = PORT_TYPE_MASK & (PORT_TYPE_NVE << PORT_TYPE_OFFSET)
CPU_MASK = PORT_TYPE_MASK & (PORT_TYPE_CPU << PORT_TYPE_OFFSET)

def is_nve(port):
    return (port & NVE_MASK) != 0

def is_cpu(port):
    return (port & CPU_MASK) != 0

def is_port_admin_status_up(log_port):
    oper_state_p = new_sx_port_oper_state_t_p()
    admin_state_p = new_sx_port_admin_state_t_p()
    module_state_p = new_sx_port_module_state_t_p()
    rc = sx_api_port_state_get(handle, log_port, oper_state_p, admin_state_p, module_state_p)
    assert rc == SXD_STATUS_SUCCESS, "sx_api_port_state_get failed, rc = %d" % rc

    admin_state = sx_port_admin_state_t_p_value(admin_state_p)
    if admin_state == SX_PORT_ADMIN_STATUS_UP:
        return True
    else:
        return False

def set_port_admin_status_by_log_port(handle, log_port, admin_status):
    rc = sx_api_port_state_set(handle, log_port, admin_status)
    assert rc == SX_STATUS_SUCCESS, "sx_api_port_state_set failed, rc = %d" % rc

# Get all the ports related to the sfp, if port admin status is up, put it to list
def get_log_ports(handle, sfp_module):
    port_attributes_list = new_sx_port_attributes_t_arr(SX_PORT_ATTR_ARR_SIZE)
    port_cnt_p = new_uint32_t_p()
    uint32_t_p_assign(port_cnt_p, SX_PORT_ATTR_ARR_SIZE)

    rc = sx_api_port_device_get(handle, DEVICE_ID , SWITCH_ID, port_attributes_list,  port_cnt_p)
    assert rc == SX_STATUS_SUCCESS, "sx_api_port_device_get failed, rc = %d" % rc

    port_cnt = uint32_t_p_value(port_cnt_p)
    log_port_list = []
    for i in range(0, port_cnt):
        port_attributes = sx_port_attributes_t_arr_getitem(port_attributes_list, i)
        if is_nve(int(port_attributes.log_port)) == False \
           and is_cpu(int(port_attributes.log_port)) == False \
           and port_attributes.port_mapping.module_port == sfp_module \
           and is_port_admin_status_up(port_attributes.log_port):
            log_port_list.append(port_attributes.log_port)

    return log_port_list

def init_sx_meta_data():
    meta = sxd_reg_meta_t()
    meta.dev_id = DEVICE_ID
    meta.swid = SWITCH_ID
    return meta

def set_sfp_admin_status(sfp_module, admin_status):
    # Get PMAOS
    pmaos = ku_pmaos_reg()
    pmaos.module = sfp_module
    meta = init_sx_meta_data()
    meta.access_cmd = SXD_ACCESS_CMD_GET
    rc = sxd_access_reg_pmaos(pmaos, meta, REGISTER_NUM, None, None)
    assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_pmaos failed, rc = %d" % rc

    # Set admin status to PMAOS
    pmaos.ase = PMAOS_ASE
    pmaos.ee = PMAOS_EE
    pmaos.e = PMAOS_E
    pmaos.rst = PMAOS_RST
    if admin_status == SX_PORT_ADMIN_STATUS_DOWN:
        pmaos.admin_status = PMAOS_DISABLE
    else:
        pmaos.admin_status = PMAOS_ENABLE

    meta.access_cmd = SXD_ACCESS_CMD_SET
    rc = sxd_access_reg_pmaos(pmaos, meta, REGISTER_NUM, None, None)
    assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_pmaos failed, rc = %d" % rc

def set_sfp_lpmode(sfp_module, lpm_enable):
    # Get PMMP
    pmmp = ku_pmmp_reg()
    pmmp.module = sfp_module
    meta = init_sx_meta_data()
    meta.access_cmd = SXD_ACCESS_CMD_GET
    rc = sxd_access_reg_pmmp(pmmp, meta, REGISTER_NUM, None, None)
    assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_pmmp failed, rc = %d" % rc

    # Set low power mode status
    lpm_mask = 1 << 8
    if lpm_enable:
        pmmp.eeprom_override = pmmp.eeprom_override | lpm_mask
    else:
        pmmp.eeprom_override = pmmp.eeprom_override & (~lpm_mask)

    meta.access_cmd = SXD_ACCESS_CMD_SET
    rc = sxd_access_reg_pmmp(pmmp, meta, REGISTER_NUM, None, None)
    assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_pmmp failed, rc = %d" % rc

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
rc = sxd_access_reg_init(pid, None, SXD_LOG_VERBOSITY_LEVEL)
if (rc != SXD_STATUS_SUCCESS):
    print "Failed to initializing register access.\nPlease check that SDK is running."
    sys.exit(errno.EACCES);

# Get SFP module
sfp_module = int(sys.argv[1]) - 1

# Get all ports at admin up status that related to the SFP module
log_port_list = get_log_ports(handle, sfp_module)

# SET SFP related ports to admin down status
for log_port in log_port_list:
    set_port_admin_status_by_log_port(handle, log_port, SX_PORT_ADMIN_STATUS_DOWN)

# Disable admin status before LPM settings
set_sfp_admin_status(sfp_module, SX_PORT_ADMIN_STATUS_DOWN)

# Set low power mode status
set_sfp_lpmode(sfp_module, lpm_enable)

# Enable admin status after LPM settings
set_sfp_admin_status(sfp_module, SX_PORT_ADMIN_STATUS_UP)

# SET SFP related ports to admin up status
for log_port in log_port_list:
    set_port_admin_status_by_log_port(handle, log_port, SX_PORT_ADMIN_STATUS_UP)

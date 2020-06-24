#!/usr/bin/env python

import sys, errno
import os
from python_sdk_api.sxd_api import *
from python_sdk_api.sx_api import *

# Check if SFP port number is provided
if len(sys.argv) < 2:
    print "SFP module number is missed."
    print "Usage: sfplpmget.py <SFP module>"
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
    sys.exit(errno.EACCES)

# Get SFP module number
sfp_module = int(sys.argv[1]) - 1

# Get MCION
mcion = ku_mcion_reg()
mcion.module = sfp_module
meta = sxd_reg_meta_t()
meta.dev_id = 1
meta.swid = 0
meta.access_cmd = SXD_ACCESS_CMD_GET

rc = sxd_access_reg_mcion(mcion, meta, 1, None, None)
assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_mcion failed, rc = %d" % rc

# Get low power mode status
lpm_mask = 1 << 8
lpm_status = (lpm_mask & mcion.module_status_bits) != 0
print "LPM ON" if lpm_status else "LPM OFF"

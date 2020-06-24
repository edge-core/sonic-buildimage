#!/usr/bin/env python

import sys, errno
import os
from python_sdk_api.sxd_api import *
from python_sdk_api.sx_api import *

# Check if SFP port number is provided
if len(sys.argv) < 2:
    print "SFP module number or LPM is missed."
    print "Usage: sfpreset.py <SFP module>"
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

# Get PMAOS
pmaos = ku_pmaos_reg()
pmaos.module = sfp_module
meta = sxd_reg_meta_t()
meta.dev_id = 1
meta.swid = 0
meta.access_cmd = SXD_ACCESS_CMD_GET

rc = sxd_access_reg_pmaos(pmaos, meta, 1, None, None)
assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_pmaos failed, rc = %d" % rc

# Reset SFP
pmaos.rst = 1
meta.access_cmd = SXD_ACCESS_CMD_SET
rc = sxd_access_reg_pmaos(pmaos, meta, 1, None, None)
assert rc == SXD_STATUS_SUCCESS, "sxd_access_reg_pmaos failed, rc = %d" % rc
print "Reset flag is set"

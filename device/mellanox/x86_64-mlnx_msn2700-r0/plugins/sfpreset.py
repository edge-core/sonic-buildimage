#!/usr/bin/env python
"""
This utility reset the given SFP module.
"""

import sys
import errno
from python_sdk_api.sx_api import *

# Check if SFP port number is provided
if len(sys.argv) < 2:
    print("SFP module number or LPM is missed.")
    print("Usage: sfpreset.py <SFP module>")
    sys.exit(errno.EINVAL)

# Init SDK API
rc, handle = sx_api_open(None)
if rc != SX_STATUS_SUCCESS:
    print("Failed to open api handle.\nPlease check that SDK is running.")
    sys.exit(errno.EACCES)

# Get SFP module number
sfp_module = int(sys.argv[1]) - 1

rc = sx_mgmt_phy_mod_reset(handle, sfp_module)
assert rc == SX_STATUS_SUCCESS, "sx_mgmt_phy_mod_reset failed, rc = %d" % rc

sx_api_close(handle)

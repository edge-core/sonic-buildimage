# mellanox firmware

MLNX_FW = fw-SPC-rel-13_1400_0126-EVB.mfa
$(MLNX_FW)_URL = $(MLNX_SDK_BASE_URL)/$(MLNX_FW)
SONIC_ONLINE_FILES += $(MLNX_FW)

export MLNX_FW

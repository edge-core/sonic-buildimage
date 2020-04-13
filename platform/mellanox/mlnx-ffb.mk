# mellanox fast fast boot script

MLNX_FFB_SCRIPT = mlnx-ffb.sh
$(MLNX_FFB_SCRIPT)_PATH = platform/mellanox/
SONIC_COPY_FILES += $(MLNX_FFB_SCRIPT)

MLNX_FILES += $(MLNX_FFB_SCRIPT)

export MLNX_FFB_SCRIPT

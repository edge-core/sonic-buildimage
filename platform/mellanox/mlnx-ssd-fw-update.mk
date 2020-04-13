# ssd update tool

MLNX_SSD_FW_UPDATE = mlnx-ssd-fw-update.sh
$(MLNX_SSD_FW_UPDATE)_PATH = platform/mellanox/
SONIC_COPY_FILES += $(MLNX_SSD_FW_UPDATE)

MLNX_FILES += $(MLNX_SSD_FW_UPDATE)

export MLNX_SSD_FW_UPDATE

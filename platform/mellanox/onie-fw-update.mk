# bios update tool

ONIE_FW_UPDATE= onie-fw-update
$(ONIE_FW_UPDATE)_PATH = platform/mellanox/
SONIC_COPY_FILES += $(ONIE_FW_UPDATE)

export ONIE_FW_UPDATE

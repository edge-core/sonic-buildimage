# Mellanox script for enabling/disabling hardware watchdog

HW_MANAGEMENT_WD_SCRIPT = hw-management-wd.sh
$(HW_MANAGEMENT_WD_SCRIPT)_PATH = platform/mellanox/
SONIC_COPY_FILES += $(HW_MANAGEMENT_WD_SCRIPT)

MLNX_FILES += $(HW_MANAGEMENT_WD_SCRIPT)

export HW_MANAGEMENT_WD_SCRIPT

# sonic-thermalctld (SONiC Thermal control daemon) Debian package

SONIC_THERMALCTLD = sonic_thermalctld-1.0-py2-none-any.whl
$(SONIC_THERMALCTLD)_SRC_PATH = $(SRC_PATH)/sonic-platform-daemons/sonic-thermalctld
$(SONIC_THERMALCTLD)_DEPENDS = $(SONIC_PY_COMMON_PY2)
$(SONIC_THERMALCTLD)_PYTHON_VERSION = 2
SONIC_PYTHON_WHEELS += $(SONIC_THERMALCTLD)

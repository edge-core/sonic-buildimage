# sonic-thermalctld (SONiC Thermal control daemon) Debian package

SONIC_THERMALCTLD = python-sonic-thermalctld_1.0-1_all.deb
$(SONIC_THERMALCTLD)_SRC_PATH = $(SRC_PATH)/sonic-platform-daemons/sonic-thermalctld
$(SONIC_THERMALCTLD)_WHEEL_DEPENDS = $(SONIC_PY_COMMON_PY2)
SONIC_PYTHON_STDEB_DEBS += $(SONIC_THERMALCTLD)

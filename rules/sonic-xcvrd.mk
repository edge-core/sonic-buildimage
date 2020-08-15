# sonic-xcvrd (SONiC Transceiver monitoring daemon) Debian package

SONIC_XCVRD = sonic_xcvrd-1.0-py2-none-any.whl
$(SONIC_XCVRD)_SRC_PATH = $(SRC_PATH)/sonic-platform-daemons/sonic-xcvrd
$(SONIC_XCVRD)_DEPENDS = $(SONIC_PY_COMMON_PY2)
$(SONIC_XCVRD)_PYTHON_VERSION = 2
SONIC_PYTHON_WHEELS += $(SONIC_XCVRD)

# sonic-pcied (SONiC PCIe Monitor daemon) Debian package

SONIC_PCIED = sonic_pcied-1.0-py2-none-any.whl
$(SONIC_PCIED)_SRC_PATH = $(SRC_PATH)/sonic-platform-daemons/sonic-pcied
$(SONIC_PCIED)_DEPENDS = $(SONIC_PY_COMMON_PY2)
$(SONIC_PCIED)_PYTHON_VERSION = 2
SONIC_PYTHON_WHEELS += $(SONIC_PCIED)

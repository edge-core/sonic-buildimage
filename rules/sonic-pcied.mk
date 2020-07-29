# sonic-pcied (SONiC PCIe Monitor daemon) Debian package

SONIC_PCIED = python-sonic-pcied_1.0-1_all.deb
$(SONIC_PCIED)_SRC_PATH = $(SRC_PATH)/sonic-platform-daemons/sonic-pcied
$(SONIC_PCIED)_WHEEL_DEPENDS = $(SONIC_DAEMON_BASE_PY2)
SONIC_PYTHON_STDEB_DEBS += $(SONIC_PCIED)

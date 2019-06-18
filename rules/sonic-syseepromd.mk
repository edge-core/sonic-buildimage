# sonic-syseepromd (SONiC Syseeprom gathering daemon) Debian package

SONIC_SYSEEPROMD = python-sonic-syseepromd_1.0-1_all.deb
$(SONIC_SYSEEPROMD)_SRC_PATH = $(SRC_PATH)/sonic-platform-daemons/sonic-syseepromd
SONIC_PYTHON_STDEB_DEBS += $(SONIC_SYSEEPROMD)

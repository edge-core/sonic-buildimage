# sonic-syseepromd (SONiC Syseeprom gathering daemon) Debian package

SONIC_SYSEEPROMD = sonic_syseepromd-1.0-py2-none-any.whl
$(SONIC_SYSEEPROMD)_SRC_PATH = $(SRC_PATH)/sonic-platform-daemons/sonic-syseepromd
$(SONIC_SYSEEPROMD)_DEPENDS = $(SONIC_PY_COMMON_PY2)
$(SONIC_SYSEEPROMD)_PYTHON_VERSION = 2
SONIC_PYTHON_WHEELS += $(SONIC_SYSEEPROMD)

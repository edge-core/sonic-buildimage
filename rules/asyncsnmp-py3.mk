# asyncsnmp python2 wheel

ASYNCSNMP_PY3 = asyncsnmp-2.1.0-py3-none-any.whl
$(ASYNCSNMP_PY3)_SRC_PATH = $(SRC_PATH)/sonic-snmpagent
$(ASYNCSNMP_PY3)_PYTHON_VERSION = 3
# Depends on sonic-platform-common so it is possible to import sonic_psu
$(ASYNCSNMP_PY3)_DEPENDS += $(SWSSSDK_PY3) $(SONIC_PLATFORM_COMMON_PY3)
SONIC_PYTHON_WHEELS += $(ASYNCSNMP_PY3)

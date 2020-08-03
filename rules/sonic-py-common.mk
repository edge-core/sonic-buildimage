# SONIC_PY_COMMON_PY2 package

SONIC_PY_COMMON_PY2 = sonic_py_common-1.0-py2-none-any.whl
$(SONIC_PY_COMMON_PY2)_SRC_PATH = $(SRC_PATH)/sonic-py-common
$(SONIC_PY_COMMON_PY2)_DEPENDS += $(SWSSSDK_PY2)
$(SONIC_PY_COMMON_PY2)_PYTHON_VERSION = 2
SONIC_PYTHON_WHEELS += $(SONIC_PY_COMMON_PY2)

# SONIC_PY_COMMON_PY3 package

SONIC_PY_COMMON_PY3 = sonic_py_common-1.0-py3-none-any.whl
$(SONIC_PY_COMMON_PY3)_SRC_PATH = $(SRC_PATH)/sonic-py-common
$(SONIC_PY_COMMON_PY3)_DEPENDS += $(SWSSSDK_PY3)
# Synthetic dependency to avoid building the Python 2 and 3 packages
# simultaneously and any potential conflicts which may arise
$(SONIC_PY_COMMON_PY3)_DEPENDS += $(SONIC_PY_COMMON_PY2)
$(SONIC_PY_COMMON_PY3)_PYTHON_VERSION = 3
SONIC_PYTHON_WHEELS += $(SONIC_PY_COMMON_PY3)

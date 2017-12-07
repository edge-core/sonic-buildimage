# sonic utilities package

SONIC_UTILS = python-sonic-utilities_1.1-1_all.deb
$(SONIC_UTILS)_SRC_PATH = $(SRC_PATH)/sonic-utilities
$(SONIC_UTILS)_WHEEL_DEPENDS = $(SONIC_CONFIG_ENGINE)
SONIC_PYTHON_STDEB_DEBS += $(SONIC_UTILS)

# Build sonic-utilities into python3 wheel, so we can use PSU code
# Note: _DEPENDS macro is not defined
SONIC_UTILS_PY3 = sonic_utilities-1.1-py3-none-any.whl
$(SONIC_UTILS_PY3)_SRC_PATH = $(SRC_PATH)/sonic-utilities
$(SONIC_UTILS_PY3)_PYTHON_VERSION = 3
$(SONIC_UTILS_PY3)_TEST = n
SONIC_PYTHON_WHEELS += $(SONIC_UTILS_PY3)

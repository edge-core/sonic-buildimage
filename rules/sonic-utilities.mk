# sonic utilities package

SONIC_UTILITIES_PY3 = sonic_utilities-1.2-py3-none-any.whl
$(SONIC_UTILITIES_PY3)_SRC_PATH = $(SRC_PATH)/sonic-utilities
$(SONIC_UTILITIES_PY3)_PYTHON_VERSION = 3
$(SONIC_UTILITIES_PY3)_DEPENDS += $(SONIC_PY_COMMON_PY3) \
                                  $(SWSSSDK_PY3) \
                                  $(SONIC_CONFIG_ENGINE_PY3) \
                                  $(SONIC_YANG_MGMT_PY3) \
                                  $(SONIC_YANG_MODELS_PY3)
$(SONIC_UTILITIES_PY3)_DEBS_DEPENDS = $(LIBYANG) \
                                      $(LIBYANG_CPP) \
                                      $(LIBYANG_PY3) \
                                      $(LIBSWSSCOMMON) \
                                      $(PYTHON3_SWSSCOMMON)
SONIC_PYTHON_WHEELS += $(SONIC_UTILITIES_PY3)

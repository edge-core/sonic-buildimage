# sonic-bgpcfgd package

SONIC_BGPCFGD = sonic_bgpcfgd-1.0-py2-none-any.whl
$(SONIC_BGPCFGD)_SRC_PATH = $(SRC_PATH)/sonic-bgpcfgd
# These dependencies are only needed becuase they are dependencies
# of sonic-config-engine and bgpcfgd explicitly calls sonic-cfggen
# as part of its unit tests.
# TODO: Refactor unit tests so that these dependencies are not needed
$(SONIC_BGPCFGD)_DEPENDS += $(SWSSSDK_PY2) $(SONIC_PY_COMMON_PY2)
$(SONIC_BGPCFGD)_PYTHON_VERSION = 2
SONIC_PYTHON_WHEELS += $(SONIC_BGPCFGD)

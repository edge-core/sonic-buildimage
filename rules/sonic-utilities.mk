# sonic utilities package
#
# NOTE: sonic-config-engine is a build-time dependency of sonic-utilities
# due to unit tests which are run during the build. However,
# sonic-platform-common and swsssdk are runtime dependencies, and should be
# added here also. However, the current build system assumes all runtime
# dependencies are .deb packages.
#

SONIC_UTILITIES_PY2 = sonic_utilities-1.2-py2-none-any.whl
$(SONIC_UTILITIES_PY2)_SRC_PATH = $(SRC_PATH)/sonic-utilities
$(SONIC_UTILITIES_PY2)_PYTHON_VERSION = 2
$(SONIC_UTILITIES_PY2)_DEPENDS += $(SONIC_PY_COMMON_PY2) \
                                  $(SONIC_PY_COMMON_PY3) \
                                  $(SWSSSDK_PY2) \
                                  $(SONIC_CONFIG_ENGINE_PY2) \
                                  $(SONIC_YANG_MGMT_PY) \
                                  $(SONIC_YANG_MODELS_PY3)
$(SONIC_UTILITIES_PY2)_DEBS_DEPENDS = $(LIBYANG) \
                                      $(LIBYANG_CPP) \
                                      $(LIBYANG_PY2) \
                                      $(LIBYANG_PY3)
SONIC_PYTHON_WHEELS += $(SONIC_UTILITIES_PY2)

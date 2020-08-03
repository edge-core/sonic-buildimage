# sonic utilities package
#
# NOTE: sonic-config-engine is a build-time dependency of sonic-utilities
# due to unit tests which are run during the build. However,
# sonic-platform-common and swsssdk are runtime dependencies, and should be
# added here also. However, the current build system assumes all runtime
# dependencies are .deb packages.
#
# TODO: Create a way to specify both .deb and .whl runtime dependencies
#       then add the aforementioned runtime dependencies here.
#

SONIC_UTILS = python-sonic-utilities_1.2-1_all.deb
$(SONIC_UTILS)_SRC_PATH = $(SRC_PATH)/sonic-utilities
$(SONIC_UTILS)_DEBS_DEPENDS = $(LIBYANG) \
                              $(LIBYANG_CPP) \
                              $(LIBYANG_PY2) \
                              $(LIBYANG_PY3)
$(SONIC_UTILS)_WHEEL_DEPENDS = $(SONIC_PY_COMMON_PY2) \
                               $(SONIC_PY_COMMON_PY3) \
                               $(SONIC_CONFIG_ENGINE) \
                               $(SONIC_YANG_MGMT_PY) \
                               $(SONIC_YANG_MODELS_PY3)
SONIC_PYTHON_STDEB_DEBS += $(SONIC_UTILS)

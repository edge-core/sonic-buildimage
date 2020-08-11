# libswsscommon package

LIBSWSSCOMMON = libswsscommon_1.0.0_$(CONFIGURED_ARCH).deb
$(LIBSWSSCOMMON)_SRC_PATH = $(SRC_PATH)/sonic-swss-common
$(LIBSWSSCOMMON)_DEPENDS += $(LIBHIREDIS_DEV) $(LIBNL3_DEV) $(LIBNL_GENL3_DEV) \
                            $(LIBNL_ROUTE3_DEV) $(LIBNL_NF3_DEV) \
                            $(LIBNL_CLI_DEV)
$(LIBSWSSCOMMON)_RDEPENDS += $(LIBHIREDIS) $(LIBNL3) $(LIBNL_GENL3) \
                             $(LIBNL_ROUTE3) $(LIBNL_NF3) $(LIBNL_CLI)
SONIC_DPKG_DEBS += $(LIBSWSSCOMMON)

LIBSWSSCOMMON_DEV = libswsscommon-dev_1.0.0_$(CONFIGURED_ARCH).deb
$(eval $(call add_derived_package,$(LIBSWSSCOMMON),$(LIBSWSSCOMMON_DEV)))

PYTHON_SWSSCOMMON = python-swsscommon_1.0.0_$(CONFIGURED_ARCH).deb
$(eval $(call add_derived_package,$(LIBSWSSCOMMON),$(PYTHON_SWSSCOMMON)))

PYTHON3_SWSSCOMMON = python3-swsscommon_1.0.0_$(CONFIGURED_ARCH).deb
$(eval $(call add_derived_package,$(LIBSWSSCOMMON),$(PYTHON3_SWSSCOMMON)))

LIBSWSSCOMMON_DBG = libswsscommon-dbg_1.0.0_$(CONFIGURED_ARCH).deb
$(LIBSWSSCOMMON_DBG)_DEPENDS += $(LIBSWSSCOMMON)
$(LIBSWSSCOMMON_DBG)_RDEPENDS += $(LIBSWSSCOMMON)
$(eval $(call add_derived_package,$(LIBSWSSCOMMON),$(LIBSWSSCOMMON_DBG)))

# The .c, .cpp, .h & .hpp files under src/{$DBG_SRC_ARCHIVE list}
# are archived into debug one image to facilitate debugging.
#
DBG_SRC_ARCHIVE += sonic-swss-common


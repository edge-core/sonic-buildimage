# radvd package

RADVD_VERSION = 2.17-2

export RADVD_VERSION

RADVD = radvd_$(RADVD_VERSION)_$(CONFIGURED_ARCH).deb
$(RADVD)_SRC_PATH = $(SRC_PATH)/radvd
SONIC_MAKE_DEBS += $(RADVD)

RADVD_DBG = radvd-dbgsym_$(RADVD_VERSION)_$(CONFIGURED_ARCH).deb
$(eval $(call add_derived_package,$(RADVD),$(RADVD_DBG)))

# The .c, .cpp, .h & .hpp files under src/{$DBG_SRC_ARCHIVE list}
# are archived into debug one image to facilitate debugging.
#
DBG_SRC_ARCHIVE += radvd

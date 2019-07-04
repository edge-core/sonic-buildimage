# libteam packages

LIBTEAM_VERSION = 1.28-1

export LIBTEAM_VERSION

LIBTEAM = libteam5_$(LIBTEAM_VERSION)_amd64.deb
$(LIBTEAM)_SRC_PATH = $(SRC_PATH)/libteam
$(LIBTEAM)_DEPENDS += $(LIBNL_GENL3_DEV) $(LIBNL_CLI_DEV)
SONIC_MAKE_DEBS += $(LIBTEAM)

LIBTEAM_DBG = libteam5-dbgsym_$(LIBTEAM_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(LIBTEAM),$(LIBTEAM_DBG)))

LIBTEAM_DEV = libteam-dev_$(LIBTEAM_VERSION)_amd64.deb
$(LIBTEAM_DEV)_DEPENDS += $(LIBTEAMDCT)
$(eval $(call add_derived_package,$(LIBTEAM),$(LIBTEAM_DEV)))

LIBTEAMDCT = libteamdctl0_$(LIBTEAM_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(LIBTEAM),$(LIBTEAMDCT)))

LIBTEAMDCT_DBG = libteamdctl0-dbgsym_$(LIBTEAM_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(LIBTEAMDCT),$(LIBTEAMDCT_DBG)))

LIBTEAM_UTILS = libteam-utils_$(LIBTEAM_VERSION)_amd64.deb
$(LIBTEAM_UTILS)_DEPENDS += $(LIBTEAMDCT)
$(eval $(call add_derived_package,$(LIBTEAM),$(LIBTEAM_UTILS)))

LIBTEAM_UTILS_DBG = libteam-utils-dbgsym_$(LIBTEAM_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(LIBTEAM_UTILS),$(LIBTEAM_UTILS_DBG)))

# The .c, .cpp, .h & .hpp files under src/{$DBG_SRC_ARCHIVE list}
# are archived into debug one image to facilitate debugging.
#
DBG_SRC_ARCHIVE += libteam

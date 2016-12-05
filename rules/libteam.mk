# libteam packages

LIBTEAM_VERSION = 1.26-1

export LIBTEAM_VERSION

LIBTEAM = libteam5_$(LIBTEAM_VERSION)_amd64.deb
$(LIBTEAM)_SRC_PATH = $(SRC_PATH)/libteam
$(LIBTEAM)_DEPENDS += $(LIBNL_GENL3_DEV) $(LIBNL_CLI_DEV)
SONIC_MAKE_DEBS += $(LIBTEAM)

LIBTEAM_DEV = libteam-dev_$(LIBTEAM_VERSION)_amd64.deb
$(LIBTEAM_DEV)_DEPENDS += $(LIBTEAMDCT)
$(eval $(call add_derived_package,$(LIBTEAM),$(LIBTEAM_DEV)))

LIBTEAMDCT = libteamdctl0_$(LIBTEAM_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(LIBTEAM),$(LIBTEAMDCT)))

LIBTEAM_UTILS = libteam-utils_$(LIBTEAM_VERSION)_amd64.deb
$(LIBTEAM_UTILS)_DEPENDS += $(LIBTEAMDCT)
$(eval $(call add_derived_package,$(LIBTEAM),$(LIBTEAM_UTILS)))

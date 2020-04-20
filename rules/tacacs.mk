# libpam-tacplus packages

PAM_TACPLUS_VERSION = 1.4.1-1

export PAM_TACPLUS_VERSION

LIBTAC2 = libtac2_$(PAM_TACPLUS_VERSION)_$(CONFIGURED_ARCH).deb
$(LIBTAC2)_SRC_PATH = $(SRC_PATH)/tacacs/pam
SONIC_MAKE_DEBS += $(LIBTAC2)

LIBPAM_TACPLUS = libpam-tacplus_$(PAM_TACPLUS_VERSION)_$(CONFIGURED_ARCH).deb
$(LIBPAM_TACPLUS)_RDEPENDS += $(LIBTAC2)
$(eval $(call add_extra_package,$(LIBTAC2),$(LIBPAM_TACPLUS)))

LIBTAC_DEV = libtac-dev_$(PAM_TACPLUS_VERSION)_$(CONFIGURED_ARCH).deb
$(LIBTAC_DEV)_DEPENDS += $(LIBTAC2)
$(eval $(call add_derived_package,$(LIBTAC2),$(LIBTAC_DEV)))



# libnss-tacplus packages
NSS_TACPLUS_VERSION = 1.0.4-1

export NSS_TACPLUS_VERSION

LIBNSS_TACPLUS = libnss-tacplus_$(NSS_TACPLUS_VERSION)_$(CONFIGURED_ARCH).deb
$(LIBNSS_TACPLUS)_DEPENDS += $(LIBTAC_DEV)
$(LIBNSS_TACPLUS)_RDEPENDS += $(LIBTAC2)
$(LIBNSS_TACPLUS)_SRC_PATH = $(SRC_PATH)/tacacs/nss
SONIC_MAKE_DEBS += $(LIBNSS_TACPLUS)

# The .c, .cpp, .h & .hpp files under src/{$DBG_SRC_ARCHIVE list}
# are archived into debug one image to facilitate debugging.
#
DBG_SRC_ARCHIVE += tacacs

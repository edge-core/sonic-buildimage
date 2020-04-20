# iccpd package

ICCPD_VERSION = 0.0.5

ICCPD = iccpd_$(ICCPD_VERSION)_amd64.deb
$(ICCPD)_DEPENDS += $(LIBNL_GENL3_DEV) $(LIBNL_CLI_DEV)
$(ICCPD)_RDEPENDS += $(LIBNL_GENL3) $(LIBNL_CLI)
$(ICCPD)_SRC_PATH = $(SRC_PATH)/iccpd
SONIC_MAKE_DEBS += $(ICCPD)

# Export these variables so they can be used in a sub-make
export ICCPD_VERSION
export ICCPD

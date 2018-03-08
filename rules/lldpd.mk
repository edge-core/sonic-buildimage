# lldpd package

LLDPD_VERSION = 0.9.5

LLDPD = lldpd_$(LLDPD_VERSION)-0_amd64.deb
$(LLDPD)_DEPENDS += $(LIBSNMP_DEV)
$(LLDPD)_RDEPENDS += $(LIBSNMP)
$(LLDPD)_SRC_PATH = $(SRC_PATH)/lldpd
SONIC_MAKE_DEBS += $(LLDPD)

LIBLLDPCTL = liblldpctl-dev_$(LLDPD_VERSION)-0_amd64.deb
$(eval $(call add_derived_package,$(LLDPD),$(LIBLLDPCTL)))

# Export these variables so they can be used in a sub-make
export LLDPD_VERSION
export LLDPD
export LIBLLDPCTL

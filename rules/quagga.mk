# quagga package

QUAGGA_VERSION_FULL = 0.99.24.1-2.1

QUAGGA = quagga_$(QUAGGA_VERSION_FULL)_amd64.deb
$(QUAGGA)_DEPENDS += $(LIBSNMP_DEV)
$(QUAGGA)_SRC_PATH = $(SRC_PATH)/sonic-quagga
SONIC_DPKG_DEBS += $(QUAGGA)

QUAGGA_DBG = quagga-dbg_$(QUAGGA_VERSION_FULL)_amd64.deb
$(eval $(call add_derived_package,$(QUAGGA),$(QUAGGA_DBG)))

# The .c, .cpp, .h & .hpp files under src/{$DBG_SRC_ARCHIVE list}
# are archived into debug one image to facilitate debugging.
#
DBG_SRC_ARCHIVE += sonic-quagga


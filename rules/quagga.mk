# quagga package

QUAGGA_VERSION_FULL = 0.99.24.1-2.1

QUAGGA = quagga_$(QUAGGA_VERSION_FULL)_$(CONFIGURED_ARCH).deb
$(QUAGGA)_DEPENDS += $(LIBSNMP_DEV)
$(QUAGGA)_SRC_PATH = $(SRC_PATH)/sonic-quagga
SONIC_DPKG_DEBS += $(QUAGGA)

QUAGGA_DBG = quagga-dbg_$(QUAGGA_VERSION_FULL)_$(CONFIGURED_ARCH).deb
$(eval $(call add_derived_package,$(QUAGGA),$(QUAGGA_DBG)))

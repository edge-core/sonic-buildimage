# quagga package

QUAGGA = quagga_0.99.24.1-2.1_amd64.deb
$(QUAGGA)_DEPENDS += $(LIBSNMP_DEV)
$(QUAGGA)_SRC_PATH = $(SRC_PATH)/sonic-quagga
SONIC_DPKG_DEBS += $(QUAGGA)

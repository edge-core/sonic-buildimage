CAVM_SAI_URL = https://github.com/XPliant/OpenXPS/raw/092461a1cf57a11132fbf8e74fa79bab3ab00f2a/SAI

CAVM_XPNET_DEB = xp80-Pcie-Endpoint.deb
$(CAVM_XPNET_DEB)_URL = $(CAVM_SAI_URL)/netdev/$(CAVM_XPNET_DEB)

SONIC_ONLINE_DEBS += $(CAVM_XPNET_DEB)

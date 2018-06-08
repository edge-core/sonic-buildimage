CAVM_SAI_URL = https://github.com/XPliant/OpenXPS/raw/d37a606cdf7d2bdc9d6ee025b758f64572f8ddbe/SAI

CAVM_XPNET_DEB = xp80-Pcie-Endpoint.deb
$(CAVM_XPNET_DEB)_URL = $(CAVM_SAI_URL)/netdev/$(CAVM_XPNET_DEB)

SONIC_ONLINE_DEBS += $(CAVM_XPNET_DEB)

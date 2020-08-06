# Centec SAI

export CENTEC_SAI_VERSION = 1.6.3-1
export CENTEC_SAI = libsai_$(CENTEC_SAI_VERSION)_$(PLATFORM_ARCH).deb

$(CENTEC_SAI)_URL = https://github.com/CentecNetworks/sonic-binaries/raw/master/$(PLATFORM_ARCH)/sai/$(CENTEC_SAI)
SONIC_ONLINE_DEBS += $(CENTEC_SAI)


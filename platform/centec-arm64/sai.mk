# Centec SAI

export CENTEC_SAI_VERSION = 1.7.1-1
export CENTEC_SAI = libsai_$(CENTEC_SAI_VERSION)_$(PLATFORM_ARCH).deb

$(CENTEC_SAI)_URL = https://github.com/CentecNetworks/sonic-binaries/raw/master/$(PLATFORM_ARCH)/sai/$(CENTEC_SAI)
$(eval $(call add_conflict_package,$(CENTEC_SAI),$(LIBSAIVS_DEV)))
SONIC_ONLINE_DEBS += $(CENTEC_SAI)


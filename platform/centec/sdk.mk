# Centec SAI
CENTEC_SAI = libsai_1.9.1-0_amd64.deb
$(CENTEC_SAI)_URL = https://github.com/CentecNetworks/sonic-binaries/raw/master/amd64/sai/$(CENTEC_SAI)
$(eval $(call add_conflict_package,$(CENTEC_SAI),$(LIBSAIVS_DEV)))

SONIC_ONLINE_DEBS += $(CENTEC_SAI)

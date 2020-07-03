# Centec SAI
CENTEC_SAI = libsai_1.6.1_amd64.deb
$(CENTEC_SAI)_URL = https://github.com/CentecNetworks/sonic-binaries/raw/master/amd64/libsai_1.6.1-1.0_amd64.deb
$(CENTEC_SAI)_CONFLICTS += $(LIBSAIVS_DEV)

SONIC_ONLINE_DEBS += $(CENTEC_SAI)

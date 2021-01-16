# Centec SAI
CENTEC_SAI = libsai_1.3.3_amd64.deb
$(CENTEC_SAI)_URL = https://github.com/CentecNetworks/goldengate-sai/raw/master/lib/SONiC_1.3.3/libsai_1.3.3-1.0_amd64.deb
$(CENTEC_SAI)_CONFLICTS += $(LIBSAIVS_DEV)

SONIC_ONLINE_DEBS += $(CENTEC_SAI)

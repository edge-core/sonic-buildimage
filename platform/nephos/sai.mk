NEPHOS_SAI = libsainps_2.0.3_sai_1.2.4_d15aca_amd64.deb
$(NEPHOS_SAI)_URL = "https://github.com/NephosInc/SONiC/raw/master/sai/libsainps_2.0.3_sai_1.2.4_d15aca_amd64.deb"

NEPHOS_SAI_DEV = libsainps-dev_2.0.3_sai_1.2.4_d15aca_amd64.deb
$(eval $(call add_derived_package,$(NEPHOS_SAI),$(NEPHOS_SAI_DEV)))
$(NEPHOS_SAI_DEV)_URL = "https://github.com/NephosInc/SONiC/raw/master/sai/libsainps-dev_2.0.3_sai_1.2.4_d15aca_amd64.deb"

SONIC_ONLINE_DEBS += $(NEPHOS_SAI) $(NEPHOS_SAI_DEV)
$(NEPHOS_SAI_DEV)_DEPENDS += $(NEPHOS_SAI)

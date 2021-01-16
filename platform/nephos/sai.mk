SDK_VERSION = 3.0.0
SAI_VERSION = 1.4.1
SAI_COMMIT_ID = 4780e5

NEPHOS_SAI = libsainps_$(SDK_VERSION)_sai_$(SAI_VERSION)_$(SAI_COMMIT_ID)_amd64.deb
$(NEPHOS_SAI)_URL = "https://github.com/NephosInc/SONiC/raw/master/sai/libsainps_$(SDK_VERSION)_sai_$(SAI_VERSION)_$(SAI_COMMIT_ID)_amd64.deb"

NEPHOS_SAI_DEV = libsainps-dev_$(SDK_VERSION)_sai_$(SAI_VERSION)_$(SAI_COMMIT_ID)_amd64.deb
$(eval $(call add_derived_package,$(NEPHOS_SAI),$(NEPHOS_SAI_DEV)))
$(NEPHOS_SAI_DEV)_URL = "https://github.com/NephosInc/SONiC/raw/master/sai/libsainps-dev_$(SDK_VERSION)_sai_$(SAI_VERSION)_$(SAI_COMMIT_ID)_amd64.deb"

SONIC_ONLINE_DEBS += $(NEPHOS_SAI) $(NEPHOS_SAI_DEV)
$(NEPHOS_SAI_DEV)_DEPENDS += $(NEPHOS_SAI)
$(NEPHOS_SAI_DEV)_CONFLICTS += $(LIBSAIVS_DEV)

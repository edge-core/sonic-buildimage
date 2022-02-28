BRCM_SAI = libsaibcm_5.0.0.12_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_5.0.0.12_amd64.deb?sv=2020-10-02&st=2022-02-25T17%3A46%3A38Z&se=2032-02-26T17%3A46%3A00Z&sr=b&sp=r&sig=GbeB32uiGwsO%2BY1XQayd1%2BjUhf64MU%2BCHKUYXkRaniQ%3D"

BRCM_SAI_DEV = libsaibcm-dev_5.0.0.12_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm-dev_5.0.0.12_amd64.deb?sv=2020-10-02&st=2022-02-25T17%3A43%3A43Z&se=2032-02-26T17%3A43%3A00Z&sr=b&sp=r&sig=hI0rLF2o%2BIuqlegLcbC%2FFAOsP3VmTcemA2tGt0dig%2Fo%3D"

# SAI module for DNX Asic family
BRCM_DNX_SAI = libsaibcm_dnx_5.0.0.12_amd64.deb
$(BRCM_DNX_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_dnx_5.0.0.12_amd64.deb?sv=2020-10-02&st=2022-02-25T17%3A47%3A45Z&se=2032-02-26T17%3A47%3A00Z&sr=b&sp=r&sig=ZzmBbHh5x1h5hWepSZsjBeaTpcxgdoPrqTZCd9i6DfE%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
SONIC_ONLINE_DEBS += $(BRCM_DNX_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

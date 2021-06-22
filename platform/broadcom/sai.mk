BRCM_SAI = libsaibcm_5.0.0.1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_5.0.0.1_amd64.deb?sv=2015-04-05&sr=b&sig=FXHu5ggw8zfUdvi0UScTHMAP0X3br0vTM4f2U2brQWo%3D&se=2029-08-15T01%3A20%3A19Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_5.0.0.1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm-dev_5.0.0.1_amd64.deb?sv=2015-04-05&sr=b&sig=C48%2BIViiA5KAq4ubDkXSehylTQgiIc7ZD47eo4roBYI%3D&se=2029-08-15T01%3A21%3A14Z&sp=r"

# SAI module for DNX Asic family
BRCM_DNX_SAI = libsaibcm_dnx_5.0.0.1_amd64.deb
$(BRCM_DNX_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_dnx_5.0.0.1_amd64.deb?sv=2015-04-05&sr=b&sig=iUW4ZSz43oeOSe21%2BFaNTG1phTr6qgAfeeEN2mCXBWU%3D&se=2035-01-17T05%3A15%3A51Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
SONIC_ONLINE_DEBS += $(BRCM_DNX_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

BRCM_SAI = libsaibcm_4.3.0.13-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm_4.3.0.13-1_amd64.deb?sv=2015-04-05&sr=b&sig=e%2BBucofzEwCC%2BclqK1OeCi5YFpQAD4ID4FfODzszsuM%3D&se=2034-10-22T06%3A00%3A14Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.0.13-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm-dev_4.3.0.13-1_amd64.deb?sv=2015-04-05&sr=b&sig=twfshldM6GQEphfU%2BQ4xmJlGJkv2Sy7KU1F72RYYM0A%3D&se=2034-10-22T06%3A00%3A45Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

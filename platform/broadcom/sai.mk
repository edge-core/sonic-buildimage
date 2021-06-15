BRCM_SAI = libsaibcm_3.7.5.2-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.5.2-3_amd64.deb?sv=2015-04-05&sr=b&sig=dvVHQluR6fJy1bo%2Bj7l8jazCq6v6fVTwGXvkWa8uoa8%3D&se=2029-09-01T22%3A07%3A34Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.5.2-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.5.2-3_amd64.deb?sv=2015-04-05&sr=b&sig=WiEoc6PuzBvtInb%2FDAV%2Bv1whOJN4zc8AC59yCXAe9Xo%3D&se=2029-09-01T22%3A06%3A25Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

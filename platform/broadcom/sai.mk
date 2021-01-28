BRCM_SAI = libsaibcm_4.3.0.10-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm_4.3.0.10-2_amd64.deb?sv=2015-04-05&sr=b&sig=1L2kJwYBuXDc9ObuVBBUS%2F%2FBVIfAA651ig5k6O1ZztE%3D&se=2022-06-10T21%3A25%3A43Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.0.10-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm-dev_4.3.0.10-2_amd64.deb?sv=2015-04-05&sr=b&sig=2Vm6o8HtbjI%2BfVoHJUiO5b75USqGra9CLSFXViQm8yM%3D&se=2022-06-10T21%3A26%3A35Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

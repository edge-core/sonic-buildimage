BRCM_SAI = libsaibcm_4.3.3.4-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm_4.3.3.4-2_amd64.deb?sv=2015-04-05&sr=b&sig=DuX9sPYncs6MySLYMFOVSIxHvaBUn%2FJaeokJi9nVUb0%3D&se=2024-01-16T14%3A30%3A20Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.3.4-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm-dev_4.3.3.4-2_amd64.deb?sv=2015-04-05&sr=b&sig=CqqazugaYvhUgsW2CkDvgJljTJL8tFT3WcDAlkIxjdY%3D&se=2024-01-16T14%3A31%3A19Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

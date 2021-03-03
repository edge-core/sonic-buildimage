BRCM_SAI = libsaibcm_3.7.5.2-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.5.2-2_amd64.deb?sv=2015-04-05&sr=b&sig=iHtJX8UWU8HmkijkYsuw3X7j6Tyoe5swaDv07nz%2BVEc%3D&se=2034-11-05T00%3A18%3A35Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.5.2-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.5.2-2_amd64.deb?sv=2015-04-05&sr=b&sig=UPlGJmD1PXGArUgvB84%2BU807HeJt1J5YTWaS%2Fq2%2FfGQ%3D&se=2034-11-05T00%3A19%3A05Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

BRCM_SAI = libsaibcm_4.3.3.3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm_4.3.3.3_amd64.deb?sv=2019-12-12&st=2021-03-18T03%3A28%3A15Z&se=2030-03-19T03%3A28%3A00Z&sr=b&sp=r&sig=YDCGJeY4Om4%2B5tkdZN%2BvWjLGh8JhsDyfMPs%2FfHgW8nA%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.3.3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm-dev_4.3.3.3_amd64.deb?sv=2019-12-12&st=2021-03-18T03%3A29%3A30Z&se=2030-03-19T03%3A29%3A00Z&sr=b&sp=r&sig=e5hvdlKvupLmWfNK%2B37LYUXfxNBm6Y%2F0%2Bnv2Aq8q51w%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

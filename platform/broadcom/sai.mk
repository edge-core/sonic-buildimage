BRCM_SAI = libsaibcm_3.7.5.1-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/master/libsaibcm_3.7.5.1-3_amd64.deb?sv=2015-04-05&sr=b&sig=hwGt%2Fw1fWhauEsCXBTBmC3vC8G90iJT4DEp%2Bznwh4WY%3D&se=2034-04-16T01%3A02%3A17Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.5.1-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/master/libsaibcm-dev_3.7.5.1-3_amd64.deb?sv=2015-04-05&sr=b&sig=nuyZOMB%2BnmDIROP60UAiDl9eG0YHAEj6u8ViTlEqjf0%3D&se=2034-04-16T01%3A01%3A51Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

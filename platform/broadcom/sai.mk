BRCM_SAI = libsaibcm_4.2.1.3-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/libsaibcm_4.2.1.3-1_amd64.deb?sv=2015-04-05&sr=b&sig=1%2BrMfgxeSc%2BXJUPw6X%2FhNGxe4KUp15Oqq1lVwMJGiW0%3D&se=2034-07-20T03%3A20%3A08Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.2.1.3-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/libsaibcm-dev_4.2.1.3-1_amd64.deb?sv=2015-04-05&sr=b&sig=lTzaCynflt5UO7Ltf2Z%2B6zHJ4R%2BFj421kupIGO4%2FOCI%3D&se=2034-07-20T03%3A19%3A27Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

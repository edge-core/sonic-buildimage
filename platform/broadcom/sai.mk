BRCM_SAI = libsaibcm_3.1.3.4-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.4-3_amd64.deb?sv=2015-04-05&sr=b&sig=B3xLAq0vI8k0HLt740baKtMxgaAQUkenS63erudlzAU%3D&se=2031-11-09T22%3A35%3A16Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.4-3_amd64.deb?sv=2015-04-05&sr=b&sig=iIVQQNj5gYGlDr8zP9YQXSaHs0o0NziijMDRFyKMfW8%3D&se=2031-11-09T22%3A34%3A14Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

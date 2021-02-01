BRCM_SAI = libsaibcm_4.3.0.10-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm_4.3.0.10-3_amd64.deb?sv=2015-04-05&sr=b&sig=snXITt%2BRq2cKD7I%2Bqr2WCbj1Ly%2FB2NM8EW3R7wc%2B1ME%3D&se=2034-10-10T06%3A30%3A07Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.0.10-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm-dev_4.3.0.10-3_amd64.deb?sv=2015-04-05&sr=b&sig=%2BfGcnKeMApru1b8aebMHT68zEc%2BCn%2BTcC27izdHNrlA%3D&se=2034-10-10T06%3A30%3A44Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

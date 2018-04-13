BRCM_SAI = libsaibcm_3.1.3.4-10_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.4-10_amd64.deb?sv=2015-04-05&sr=b&sig=72n19AElVmbqo3ahrEFVBwMgR%2FoQ7fhUj4tcadx8pVE%3D&se=2031-12-20T20%3A27%3A14Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-10_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.4-10_amd64.deb?sv=2015-04-05&sr=b&sig=cN4qsWX8XW04ZObBDonwh5Uzgmp5A0iRBkpZA9N5Zb8%3D&se=2031-12-20T20%3A26%3A45Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

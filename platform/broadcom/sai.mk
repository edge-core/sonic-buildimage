BRCM_SAI = libsaibcm_3.1.3.5_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.5_amd64.deb?sv=2015-04-05&sr=b&sig=ui%2FF8c4fZOCqWp6KkYLvsJrJtfuWVmBCQkQWJgcyD%2FE%3D&se=2032-03-13T22%3A02%3A37Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.5_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.5_amd64.deb?sv=2015-04-05&sr=b&sig=Yk%2Bg8x84m8MBFJKSVmoPAkPFR6BCqmTrGlLY89JXGe8%3D&se=2032-03-13T22%3A03%3A27Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

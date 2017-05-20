BRCM_SAI = libsaibcm_2.1.5.1-7-20170519212441.39_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-7-20170519212441.39_amd64.deb?sv=2015-04-05&sr=b&sig=CVc9ldYoy6xdUY0mKg4Rqz4uNDgkTUrPOw1ULrxa8N4%3D&se=2031-01-26T21%3A38%3A42Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-7-20170519212441.39_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-7-20170519212441.39_amd64.deb?sv=2015-04-05&sr=b&sig=xzCr9xLGF3IaNK8aQGVeU4jY7YkqNEdYAuq5IP2uQM4%3D&se=2031-01-26T21%3A38%3A16Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

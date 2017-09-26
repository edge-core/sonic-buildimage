BRCM_SAI = libsaibcm_3.0.3.2-4_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.2-4_amd64.deb?sv=2015-04-05&sr=b&sig=8LE5JB9YlYHVWFf0QF5vFF7fCUbpo14OXokBi%2BKb9GI%3D&se=2031-06-04T20%3A15%3A13Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.2-4_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.2-4_amd64.deb?sv=2015-04-05&sr=b&sig=UGqSnxGtIxFBdO%2FDcFbZdPFgBPN695JQ6hLP5mBOt7g%3D&se=2031-06-04T20%3A15%3A26Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

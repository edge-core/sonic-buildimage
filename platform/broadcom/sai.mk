BRCM_SAI = libsaibcm_3.3.5.4-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm_3.3.5.4-1_amd64.deb?sv=2015-04-05&sr=b&sig=fjyImKBuCbR8x48tzRhx32tfnDq1kk1VsCJblaXh8U4%3D&se=2032-12-10T01%3A43%3A35Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.3.5.4-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm-dev_3.3.5.4-1_amd64.deb?sv=2015-04-05&sr=b&sig=91u8Og2PHD2ig%2BlIyi6UlXQ8rMSxz%2FUeJdyy%2BhecvrE%3D&se=2032-12-10T01%3A43%3A16Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

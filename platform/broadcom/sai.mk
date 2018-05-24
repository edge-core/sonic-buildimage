BRCM_SAI = libsaibcm_3.1.3.4-12_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.4-12_amd64.deb?sv=2015-04-05&sr=b&sig=iK79gjz8GQnPLU8OSxgzw35MzqmxwAXQg2N%2BalLUos0%3D&se=2032-01-31T20%3A36%3A51Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-12_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.4-12_amd64.deb?sv=2015-04-05&sr=b&sig=tSBPnK%2BK9axdPbkWP19r5ngM0ggRTWWijUIKTl8WNW0%3D&se=2032-01-31T20%3A36%3A11Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

BRCM_SAI = libsaibcm_3.7.5.1-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.5.1-1_amd64.deb?sv=2015-04-05&sr=b&sig=cxmXsJ%2BjcnR9ckFRbMigIbkzOncYkiV04weL%2FVPKBmk%3D&se=2034-03-06T00%3A30%3A30Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.5.1-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.5.1-1_amd64.deb?sv=2015-04-05&sr=b&sig=LVgghAv75VG4idW6xfpId%2FlrvPBja7uBQeTbjZsR3CA%3D&se=2034-03-06T00%3A31%3A30Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

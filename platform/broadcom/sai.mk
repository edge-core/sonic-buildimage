BRCM_SAI = libsaibcm_3.5.3.1-15_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm_3.5.3.1-15_amd64.deb?sv=2015-04-05&sr=b&sig=tZ1NxKEojTqKya6uPoAHckAhcUrV2qegAyp2goN1Yms%3D&se=2033-05-22T17%3A22%3A02Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.1-15_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm-dev_3.5.3.1-15_amd64.deb?sv=2015-04-05&sr=b&sig=1buFitrRydJ01Y%2BvmeUYveb1R1UAEQOiYMwgcyPZikw%3D&se=2033-05-22T17%3A21%3A38Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

BRCM_SAI = libsaibcm_4.3.7.0_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.7.0_amd64.deb?sv=2020-08-04&st=2022-08-10T09%3A20%3A43Z&se=2037-08-11T09%3A20%3A00Z&sr=b&sp=r&sig=T%2FHU25LsKmG5jzXLN%2BXlVXAJFg%2Bv0bfvL%2FNITpRNDyA%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.7.0_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.7.0_amd64.deb?sv=2020-08-04&st=2022-08-10T09%3A20%3A59Z&se=2037-08-11T09%3A20%3A00Z&sr=b&sp=r&sig=0gWqYSKVRW1h8If5CS63QjwlMt%2F1sCQcFbmFd6WTxeU%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

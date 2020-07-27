BRCM_SAI = libsaibcm_3.7.5.2-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.5.2-1_amd64.deb?sv=2015-04-05&sr=b&sig=9nPXIgFsF3GsypmaSUV2cZ1t2FQbInjfahVLX64%2BinQ%3D&se=2034-09-15T20%3A34%3A43Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.5.2-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.5.2-1_amd64.deb?sv=2015-04-05&sr=b&sig=SCd4ZhnKQX3SGFIpClVMWp5%2FgJtAXFtDXzUClMV3AOA%3D&se=2034-09-15T20%3A35%3A22Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

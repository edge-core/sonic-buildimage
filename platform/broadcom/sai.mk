BRCM_SAI = libsaibcm_3.1.3.4-23_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.4-23_amd64.deb?sv=2015-04-05&sr=b&sig=VmgeysdXcAhMAQO2rpMhYPhx%2BI6YDm06%2Bx4FTj2nnsA%3D&se=2033-01-19T18%3A10%3A19Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-23_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.4-23_amd64.deb?sv=2015-04-05&sr=b&sig=OOgj5GJdWN8Ga0bNvoNIfK8%2Brr0WJxwa2RCuCCbPcDs%3D&se=2033-01-19T18%3A10%3A44Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

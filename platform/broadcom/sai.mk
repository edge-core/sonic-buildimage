BRCM_SAI = libsaibcm_3.0.3.3-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.3-1_amd64.deb?sv=2015-04-05&sr=b&sig=hoUotiQsgVMo6%2BzH87aaIeTsqPsRYWQT5oRdSc1uEm8%3D&se=2154-11-09T08%3A09%3A33Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.3-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.3-1_amd64.deb?sv=2015-04-05&sr=b&sig=LfvM2LkGj3dPnSCyVEgPA35jvjKOgq%2FNSvj2UiPeGm4%3D&se=2154-11-09T08%3A11%3A03Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

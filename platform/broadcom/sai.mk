BRCM_SAI = libsaibcm_3.1.3.4-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.4-2_amd64.deb?sv=2015-04-05&sr=b&sig=EZRvr20FafC1pB3SLyA4K0cAsbbiNGPkuCuvPEgOtmU%3D&se=2031-11-01T00%3A33%3A10Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.4-2_amd64.deb?sv=2015-04-05&sr=b&sig=SXh77LQCpwF6e65rU0RX4zMSNMlAHh1iSjsLktrE360%3D&se=2031-11-01T00%3A32%3A36Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

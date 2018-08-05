BRCM_SAI = libsaibcm_3.1.3.5-5_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.5-5_amd64.deb?sv=2015-04-05&sr=b&sig=QPeazVTcPxPiWnLQRX4BqAAoyo0kTXJlfNAAtp2nilk%3D&se=2155-06-28T00%3A35%3A53Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.5-5_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.5-5_amd64.deb?sv=2015-04-05&sr=b&sig=6yrT5BVHkTr5955Rf9sADlVVN8o8TzxSjoj3JZg6nHw%3D&se=2155-06-28T00%3A37%3A34Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

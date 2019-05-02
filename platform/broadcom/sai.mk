BRCM_SAI = libsaibcm_3.1.3.4-22_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.4-22_amd64.deb?sv=2015-04-05&sr=b&sig=PXRtXh3GfOKAOky%2FBmeJYeM2H8GcdVsZFBE9%2FHNOPPQ%3D&se=2033-01-08T01%3A54%3A13Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-22_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.4-22_amd64.deb?sv=2015-04-05&sr=b&sig=6EXfCbMQwjMYDoNzI81pBb%2B%2Fz8pcCMQoAQzaiND71Cs%3D&se=2033-01-08T01%3A55%3A36Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

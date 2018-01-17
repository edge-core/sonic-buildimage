BRCM_SAI = libsaibcm_3.0.3.3-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.3-3_amd64.deb?sv=2015-04-05&sr=b&sig=A%2Bcq%2B8XL%2BZfhOV6zqwRWm1jQ31PN0t54H9abZSRwTVw%3D&se=2031-09-25T22%3A41%3A43Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.3-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.3-3_amd64.deb?sv=2015-04-05&sr=b&sig=XT0v%2B25LZ5whTwH%2FE%2FykQLV8Kzn%2FoDyLNXjmqNuiFPo%3D&se=2031-09-25T22%3A41%3A21Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

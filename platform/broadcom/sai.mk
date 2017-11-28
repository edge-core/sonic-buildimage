BRCM_SAI = libsaibcm_3.0.3.2-15_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.2-15_amd64.deb?sv=2015-04-05&sr=b&sig=U1jDC%2FrbcCn3KgZsP9GoKFa9PtyXhliMd9iJrx8%2B%2F5M%3D&se=2031-08-07T00%3A51%3A44Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.2-15_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.2-15_amd64.deb?sv=2015-04-05&sr=b&sig=nLvctIrLerXpG0SdQisirbOn1OBNLKl%2BQ7xLHRzgczM%3D&se=2031-08-07T00%3A52%3A02Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

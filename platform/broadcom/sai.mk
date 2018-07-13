BRCM_SAI = libsaibcm_3.1.3.5-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.5-3_amd64.deb?sv=2015-04-05&sr=b&sig=lzB9IHpJuMEENr9N9W0LBFamJ7mpvRVWgigfQmpIrPc%3D&se=2155-06-05T09%3A13%3A41Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.5-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.5-3_amd64.deb?sv=2015-04-05&sr=b&sig=WoRAz6j8G3Xk%2BT3MOmhp5f%2BvWggw%2BgGgk2JtDJHkKjs%3D&se=2155-06-05T09%3A14%3A46Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

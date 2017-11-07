BRCM_SAI = libsaibcm_3.0.3.2-11_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.2-11_amd64.deb?sv=2015-04-05&sr=b&sig=sXvf3ejJ8npF9iPfkTIYUneN4N8wvHKo2V6A8YoTbhk%3D&se=2031-07-17T23%3A08%3A43Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.2-11_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.2-11_amd64.deb?sv=2015-04-05&sr=b&sig=Q%2FSC7B0xDuhvHGL7GERoOw483nv6hkAQrDUaabS9JOs%3D&se=2031-07-17T23%3A09%3A08Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

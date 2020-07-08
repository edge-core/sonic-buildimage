BRCM_SAI = libsaibcm_3.7.5.1-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.5.1-2_amd64.deb?sv=2015-04-05&sr=b&sig=NMXmDm7ME%2BDN9n4kw6wXgIVmIjRifu%2FWV0UbLU9qllw%3D&se=2034-03-17T05%3A53%3A29Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.5.1-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.5.1-2_amd64.deb?sv=2015-04-05&sr=b&sig=3Q8S5fwg7WV%2BCKVwMALrf8dpQWK2cSD4J4zxbVht%2BT8%3D&se=2034-03-17T05%3A54%3A05Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

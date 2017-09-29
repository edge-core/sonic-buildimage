BRCM_SAI = libsaibcm_3.0.3.2-5_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.2-5_amd64.deb?sv=2015-04-05&sr=b&sig=MQE6FrxHs%2BIUPjRaSpWagcSjY6bbHLCUYasusxILkEs%3D&se=2031-06-07T21%3A50%3A36Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.2-5_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.2-5_amd64.deb?sv=2015-04-05&sr=b&sig=o8bjWlxxYAM%2F95aSshRFJE57JwKVjRaH4jDU2lDEoMg%3D&se=2031-06-07T21%3A50%3A19Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

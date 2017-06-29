BRCM_SAI = libsaibcm_2.1.5.1-14-20170627090913.47_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-14-20170627090913.47_amd64.deb?sv=2015-04-05&sr=b&sig=MqrcsnIaaFfekaAqcjgbi0mDl94BJ9eRsslLJrp23q8%3D&se=2031-03-06T22%3A29%3A19Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-14-20170627090913.47_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-14-20170627090913.47_amd64.deb?sv=2015-04-05&sr=b&sig=GyAwaEdgSFGXbbFq%2FN2RgSKQ5%2Fc73NgxKMMKq3RVZw0%3D&se=2031-03-06T22%3A29%3A48Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

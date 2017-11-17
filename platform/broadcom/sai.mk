BRCM_SAI = libsaibcm_3.0.3.2-13_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.2-13_amd64.deb?sv=2015-04-05&sr=b&sig=YeXV0av6rUxy3s5VlQf4wsv6dLOKIGkkkP8lldlGr00%3D&se=2031-07-27T07%3A49%3A38Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.2-13_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.2-13_amd64.deb?sv=2015-04-05&sr=b&sig=u4dKbtc%2FAvlqq7l7BT9WcmLVEsWoV1LqOxSbBy0CkiA%3D&se=2031-07-27T07%3A50%3A08Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

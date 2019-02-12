BRCM_SAI = libsaibcm_3.1.3.4-19_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.4-19_amd64.deb?sv=2015-04-05&sr=b&sig=tbjRGxCW644D0kAuVsl2WQLj99vlb0dKgizE6TpoYjw%3D&se=2032-10-21T03%3A08%3A33Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-19_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.4-19_amd64.deb?sv=2015-04-05&sr=b&sig=AIteLXKhrlbhY661nG1LihraEu31j5G9J%2FLsFETfXvc%3D&se=2032-10-21T03%3A09%3A32Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

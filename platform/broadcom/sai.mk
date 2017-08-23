BRCM_SAI = libsaibcm_2.1.5.1-17_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-17_amd64.deb?sv=2015-04-05&sr=b&sig=6sJ4dd%2FF1hqStNQk5Z6d%2BYQGRZxLDihXRl60EeN7agc%3D&se=2031-05-02T09%3A37%3A54Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-17_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-17_amd64.deb?sv=2015-04-05&sr=b&sig=syV0rie0L2Dn4lhmndCTyCTgXQv8DPoWD3IxtlSdeNo%3D&se=2031-05-02T09%3A37%3A18Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

BRCM_SAI = libsaibcm_3.0.3.2-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.2-2_amd64.deb?sv=2015-04-05&sr=b&sig=A9GjUgI9%2B7kRQHsCFqH07iRQLhdkwSH5tvSXepb3b%2BA%3D&se=2031-05-30T22%3A47%3A47Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.2-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.2-2_amd64.deb?sv=2015-04-05&sr=b&sig=lDIwnDNHIA0WKc5ggTA4x3pVmBIM%2Bdib0hR7H1qyTe0%3D&se=2031-05-30T22%3A48%3A07Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

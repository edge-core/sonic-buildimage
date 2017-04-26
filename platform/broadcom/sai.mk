BRCM_SAI = libsaibcm_2.1.5.1-3-20170426013947.22_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-3-20170426013947.22_amd64.deb?sv=2015-04-05&sr=b&sig=nhMTShwA1OeKoLNWcIY0wMyuiDSdKYWTH%2BJGlr%2BpgU4%3D&se=2031-01-03T01%3A43%3A35Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-3-20170426013947.22_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-3-20170426013947.22_amd64.deb?sv=2015-04-05&sr=b&sig=c4%2B6zRDuA%2BTeLr3MPkAqsuvG%2BAg9cd7ffgpp2mhl9bM%3D&se=2031-01-03T01%3A43%3A08Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

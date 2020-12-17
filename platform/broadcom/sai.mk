BRCM_SAI = libsaibcm_4.2.1.5-6_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/buster/libsaibcm_4.2.1.5-6_amd64.deb?sv=2019-12-12&st=2020-12-15T06%3A40%3A06Z&se=2035-12-16T06%3A40%3A00Z&sr=b&sp=r&sig=aux78f4Uhmh2AHJqZh1GMWPYdQDWI3fVLgLmFXrpbFQ%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.2.1.5-6_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/buster/libsaibcm-dev_4.2.1.5-6_amd64.deb?sv=2019-12-12&st=2020-12-15T06%3A40%3A46Z&se=2035-12-16T06%3A40%3A00Z&sr=b&sp=r&sig=%2BnflSlIa9cIMPr%2BDmZLYtO2rhXwdDwv7Z%2BqY5MUlIM0%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

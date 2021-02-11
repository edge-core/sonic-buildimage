BRCM_SAI = libsaibcm_4.3.0.13_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm_4.3.0.13_amd64.deb?sv=2019-12-12&st=2021-02-11T06%3A07%3A09Z&se=2030-02-12T06%3A07%3A00Z&sr=b&sp=r&sig=IlCyw1BGN0Ei56tPPeXJSucFSFj8SSqUGLB2A%2BRZ1w0%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.0.13_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm-dev_4.3.0.13_amd64.deb?sv=2019-12-12&st=2021-02-11T06%3A08%3A31Z&se=2030-02-12T06%3A08%3A00Z&sr=b&sp=r&sig=G5mYUa8gCnDNpuadvHEuH%2B4q2MuY0JYspPLt2gaC2NY%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

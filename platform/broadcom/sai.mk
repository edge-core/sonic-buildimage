BRCM_SAI = libsaibcm_4.2.1.5-7_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/buster/libsaibcm_4.2.1.5-7_amd64.deb?sv=2015-04-05&sr=b&sig=ldUfPMl4Lb0KhXtVtwzFZFYU5qrhxFzT90NX3KSnku0%3D&se=2034-08-27T01%3A34%3A16Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.2.1.5-7_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/buster/libsaibcm-dev_4.2.1.5-7_amd64.deb?sv=2015-04-05&sr=b&sig=TboOe3jFGgl2j7%2FAFiJNQ%2F%2Fa4JaVGijgAH2MSMVPYOI%3D&se=2034-08-27T01%3A32%3A58Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

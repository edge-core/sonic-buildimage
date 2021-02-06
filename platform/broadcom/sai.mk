BRCM_SAI = libsaibcm_4.2.1.5-10_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/buster/libsaibcm_4.2.1.5-10_amd64.deb?sv=2019-12-12&st=2021-01-12T07%3A30%3A31Z&se=2035-01-13T07%3A30%3A00Z&sr=b&sp=r&sig=yCGwk%2FW%2Fg%2FaFxhr0oNSTZ%2BVy5B6kX1WDEsbbyz9J088%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.2.1.5-10_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/buster/libsaibcm-dev_4.2.1.5-10_amd64.deb?sv=2019-12-12&st=2021-01-12T07%3A32%3A43Z&se=2035-01-13T07%3A32%3A00Z&sr=b&sp=r&sig=wuCNc6pa12JQCBi%2BM9rLWvVI92ldan9hKNF%2BfVfUWN8%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

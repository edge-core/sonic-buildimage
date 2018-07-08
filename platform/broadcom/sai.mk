BRCM_SAI = libsaibcm_3.1.3.5-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.5-1_amd64.deb?sv=2015-04-05&sr=b&sig=iakBOA9VRsMmdbZWDEsQNLix%2B41gnnVX75YV%2F7VGqNU%3D&se=2155-05-31T10%3A05%3A28Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.5-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.5-1_amd64.deb?sv=2015-04-05&sr=b&sig=XipVKYmbKC%2BjrKc67BPoqhXiVSU5IF6PiF37P%2BxRxMk%3D&se=2155-05-31T10%3A07%3A38Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

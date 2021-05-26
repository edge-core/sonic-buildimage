BRCM_SAI = libsaibcm_3.5.3.7-4_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm_3.5.3.7-4_amd64.deb?sv=2019-10-10&st=2021-05-26T21%3A31%3A40Z&se=2036-05-27T21%3A31%3A00Z&sr=b&sp=r&sig=MC92N%2F9YTixBoFIEgDtJHO9iEv2xcKklXm2qDH4QoJc%3D"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.7-4_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm-dev_3.5.3.7-4_amd64.deb?sv=2019-10-10&st=2021-05-26T21%3A30%3A47Z&se=2036-05-27T21%3A30%3A00Z&sr=b&sp=r&sig=Y0vMTykm7FlCH4R%2F95kXRYNA8%2B2OGzNr%2B6%2BoVtYK0ms%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

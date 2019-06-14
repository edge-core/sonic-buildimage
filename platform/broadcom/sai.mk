BRCM_SAI = libsaibcm_3.3.6.1-9_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm_3.3.6.1-9_amd64.deb?sv=2015-04-05&sr=b&sig=ZsZxC0bmXIX9PCa73BpyMatePq8m2jWvCahFx3OJ%2F8I%3D&se=2033-02-13T21%3A31%3A33Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.3.6.1-9_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm-dev_3.3.6.1-9_amd64.deb?sv=2015-04-05&sr=b&sig=RUAbTNEcmaSvNeAKz%2F8x06hPC%2BS%2BVlGPA2%2FiwHZMF4o%3D&se=2033-02-13T21%3A31%3A02Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

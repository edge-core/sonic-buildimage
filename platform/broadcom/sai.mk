BRCM_SAI = libsaibcm_3.1.3.4-17_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.4-17_amd64.deb?sv=2015-04-05&sr=b&sig=wDTUZwUF05gxdoB%2BHVZeB8uQQWq3qFmvM5VLliLHA8E%3D&se=2155-08-17T07%3A45%3A56Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-17_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.4-17_amd64.deb?sv=2015-04-05&sr=b&sig=l%2Bvb%2F4%2FCB8IEz70msUGMYsWCpeDPp7slxwZeiKqnNAo%3D&se=2155-08-17T07%3A43%3A58Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

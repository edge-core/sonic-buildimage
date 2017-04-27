BRCM_SAI = libsaibcm_2.1.5.1-4~20170427032904.25_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-4~20170427032904.25_amd64.deb?sv=2015-04-05&sr=b&sig=NqmcwFHarhYwoV6WTou8wGbEMCoXZUdPXuegPUDpwU0%3D&se=2154-03-20T05%3A16%3A44Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-4~20170427032904.25_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-4~20170427032904.25_amd64.deb?sv=2015-04-05&sr=b&sig=8RErjP5TGdXqENcTbVrgQbvVAexMt4b%2BjU2BXFb4%2B0M%3D&se=2154-03-20T05%3A16%3A07Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

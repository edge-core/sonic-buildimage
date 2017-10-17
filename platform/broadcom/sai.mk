BRCM_SAI = libsaibcm_3.0.3.2-6_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.2-6_amd64.deb?sv=2015-04-05&sr=b&sig=78jpXMULiubmup2PBYzM5MCrt7KIHA913FlDOsdgmGY%3D&se=2031-06-25T21%3A52%3A36Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.2-6_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.2-6_amd64.deb?sv=2015-04-05&sr=b&sig=Vg%2BjJpwyJ3smRBaNVkbWH4xkNGOn%2BOxI0w3VcDgAxV0%3D&se=2031-06-25T21%3A52%3A54Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

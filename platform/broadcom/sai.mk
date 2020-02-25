BRCM_SAI = libsaibcm_3.7.3.3-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.3.3-2_amd64.deb?sv=2015-04-05&sr=b&sig=701AT0Rwcn%2FKT33UPE1TTQRoJ9tQG0iDfOSXXVCtnyY%3D&se=2033-10-29T22%3A32%3A29Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.7.3.3-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.3.3-2_amd64.deb?sv=2015-04-05&sr=b&sig=vXdUpaP0o71SatqEoqqDH2kai%2FLuFUWZWZAy7HKfeiQ%3D&se=2033-10-29T22%3A31%3A07Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

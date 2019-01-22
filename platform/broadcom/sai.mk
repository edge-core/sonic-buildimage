BRCM_SAI = libsaibcm_3.3.4.3-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm_3.3.4.3-1_amd64.deb?sv=2015-04-05&sr=b&sig=eqQ%2BzMqpkcr8mnztwUPfUsmaWL%2Fvj0Cr2hCvALNXLtQ%3D&se=2032-09-26T21%3A45%3A32Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.3.4.3-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm-dev_3.3.4.3-1_amd64.deb?sv=2015-04-05&sr=b&sig=v7XeVaxL8H1BDsHUDtyvFIfaWrW9LILA2IEo3YypZSA%3D&se=2032-09-26T21%3A45%3A09Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

BRCM_SAI = libsaibcm_2.1.3.1-1-20170208221802.12_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.3.1-1-20170208221802.12_amd64.deb?sv=2015-04-05&sr=b&sig=RpHs7rvOiM%2FzBHeaA2BwP4CYRmiJFhPGBn88Hx9V5Rg%3D&se=2030-10-25T02%3A43%3A53Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.3.1-1-20170208221802.12_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.3.1-1-20170208221802.12_amd64.deb?sv=2015-04-05&sr=b&sig=DNOUenzhSfCHR4QdxkNwf5zdoecCblClau4rjoa0oJE%3D&se=2030-10-25T02%3A47%3A33Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

BRCM_SAI = libsaibcm_4.3.3.4-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm_4.3.3.4-1_amd64.deb?sv=2019-12-12&st=2021-04-16T16%3A07%3A16Z&se=2030-04-17T16%3A07%3A00Z&sr=b&sp=r&sig=BiY2sN%2FVvDzZlxPEGWMwMLeB725yCvwrORHULdnWyXU%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.3.4-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm-dev_4.3.3.4-1_amd64.deb?sv=2019-12-12&st=2021-04-16T16%3A07%3A55Z&se=2030-04-17T16%3A07%3A00Z&sr=b&sp=r&sig=XVNsLj8QwhGN3sgvgvPZ2glnLZm9Dhyci%2F61k36Fl0c%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

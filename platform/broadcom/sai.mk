BRCM_SAI = libsaibcm_4.3.7.1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.7.1_amd64.deb?sv=2020-08-04&st=2022-09-14T09%3A37%3A35Z&se=2037-09-15T09%3A37%3A00Z&sr=b&sp=r&sig=Yb9q50mb5E0A9mAj8DEc7xfc1WHdW1tyqi5OdAjUSec%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.7.1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.7.1_amd64.deb?sv=2020-08-04&st=2022-09-14T09%3A38%3A00Z&se=2037-09-15T09%3A38%3A00Z&sr=b&sp=r&sig=woY1S03ENzUKUG0htzuIaPl%2ByV0dSOm2QsimPDBhGpw%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

BRCM_SAI = libsaibcm_4.3.3.7_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.3.7_amd64.deb?sv=2015-04-05&sr=b&sig=g2jgs1YZk3CXk4vyY0gaWhHZB9hfJBiHbJ0P0BNHFB4%3D&se=2035-02-18T05%3A53%3A40Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.3.7_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.3.7_amd64.deb?sv=2015-04-05&sr=b&sig=tDjHGUadHf9xr%2FcJ8DWYzv%2Fbj%2FDsTA%2FCtdJYsRXpiQQ%3D&se=2035-02-18T05%3A54%3A26Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

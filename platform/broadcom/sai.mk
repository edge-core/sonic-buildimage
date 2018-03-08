BRCM_SAI = libsaibcm_3.1.3.4-4_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.4-4_amd64.deb?sv=2015-04-05&sr=b&sig=hSWtsH1f5FIV7rk4%2FJA99S%2B7HoJ%2BSvHN8fPXZNnO6mI%3D&se=2031-11-15T03%3A11%3A01Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-4_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.4-4_amd64.deb?sv=2015-04-05&sr=b&sig=nEo71IhiVDrk2ydJf3ejyZvQ5QES%2BxjWdQ5SEOOyaic%3D&se=2031-11-15T03%3A10%3A12Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

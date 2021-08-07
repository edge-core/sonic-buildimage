BRCM_SAI = libsaibcm_3.7.6.1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.6.1_amd64.deb?sv=2015-04-05&sr=b&sig=PXZNHvLaofj6qevZqf3eDUX7SGp%2BJnblyEV%2FkMFcwus%3D&se=2035-04-15T19%3A36%3A16Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.6.1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.6.1_amd64.deb?sv=2015-04-05&sr=b&sig=S67%2FNP8J2xshBYhDV6NwP7LBnvyUOO1EZKspL1O6bCY%3D&se=2035-04-15T19%3A37%3A50Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

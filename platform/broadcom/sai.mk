BRCM_SAI = libsaibcm_3.7.3.3-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.3.3-3_amd64.deb?sv=2015-04-05&sr=b&sig=1MS77TFH1wpXHIQuxvysznffb8shDJa7QWTCpXX3qH4%3D&se=2033-11-14T01%3A39%3A44Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.7.3.3-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.3.3-3_amd64.deb?sv=2015-04-05&sr=b&sig=Y%2FXr6tZPrUQn5bLZqXYr6Nba%2BBbhz8lJdXyNEKZ3Sh8%3D&se=2033-11-14T01%3A44%3A38Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

BRCM_SAI = libsaibcm_3.5.3.1-15_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/libsaibcm_3.5.3.1-15_amd64.deb?sv=2015-04-05&sr=b&sig=zXY%2FK%2FeGlxteIFlEkPdE%2FNDRet5T%2Fc1LgL0qyX9%2FmfQ%3D&se=2033-06-03T17%3A45%3A51Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.1-15_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/libsaibcm-dev_3.5.3.1-15_amd64.deb?sv=2015-04-05&sr=b&sig=%2BYOVgRo6dLxv3sLb8JE1wLoD%2FneYDABadwFv5xH3XRE%3D&se=2033-06-03T17%3A46%3A14Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

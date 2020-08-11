BRCM_SAI = libsaibcm_3.7.5.1-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.5.1-3_amd64.deb?sv=2015-04-05&sr=b&sig=jKyO230pW7whAMsTPZeUvcCjfE7sFin5JKzdvKswgKQ%3D&se=2034-04-19T15%3A59%3A16Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.5.1-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.5.1-3_amd64.deb?sv=2015-04-05&sr=b&sig=eqVrbb2kbr%2Bz4B8OeyJ2mchjOL70Og9W0demES3uCF0%3D&se=2034-04-19T16%3A00%3A02Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

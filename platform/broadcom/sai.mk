BRCM_SAI = libsaibcm_4.3.7.1-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.7.1-2_amd64.deb?sv=2020-04-08&st=2022-10-07T02%3A22%3A15Z&se=2037-10-08T02%3A22%3A00Z&sr=b&sp=r&sig=T2JdAgBr%2BZs29mfFQrA6KHWwkhcGgnv7MgIsml3qTNY%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.7.1-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.7.1-2_amd64.deb?sv=2020-04-08&st=2022-10-07T02%3A23%3A49Z&se=2037-10-08T02%3A23%3A00Z&sr=b&sp=r&sig=tS%2FDMtSSLNZtUsTK0QiV9mHIae7i5mwtWiqy5ZpmOnY%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

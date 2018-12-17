BRCM_SAI = libsaibcm_3.3.3.1-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm_3.3.3.1-3_amd64.deb?sv=2015-04-05&sr=b&sig=LcClnc7O9BUMfh6nYVNr76UAjLxVMtGztoH24qcY5rk%3D&se=2032-08-24T21%3A56%3A57Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.3.3.1-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm-dev_3.3.3.1-3_amd64.deb?sv=2015-04-05&sr=b&sig=OS4wTDTjFVZMFKKFx0hKtZEKUDbOyLO69gqIUaM3I4M%3D&se=2032-08-24T21%3A56%3A25Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

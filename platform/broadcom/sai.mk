BRCM_SAI = libsaibcm_4.3.5.3-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.5.3-2_amd64.deb?sv=2015-04-05&sr=b&sig=0okWyK4w%2FgsZ41OXDfxd7Nm7KFKts3W9%2FX3aLBtiVIE%3D&se=2035-11-11T03%3A30%3A32Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.5.3-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.5.3-2_amd64.deb?sv=2015-04-05&sr=b&sig=uTQVVAhHHJ2m4WQYnrsUcyq%2FIoUOcQlD4Kh52R7OSrg%3D&se=2035-11-11T03%3A32%3A33Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

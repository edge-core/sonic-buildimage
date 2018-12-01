BRCM_SAI = libsaibcm_3.3.3.1-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm_3.3.3.1-1_amd64.deb?sv=2015-04-05&sr=b&sig=Kp6Pjrvt9DD8fThhSjzDJNuVRYuW6aLwi2bgegM0hd8%3D&se=2032-08-09T02%3A22%3A31Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.3.3.1-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm-dev_3.3.3.1-1_amd64.deb?sv=2015-04-05&sr=b&sig=fTWUp3gOcNQNT9sS66CSEyP0JkSlPHNRlsvG4L64I0g%3D&se=2032-08-09T02%3A22%3A08Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

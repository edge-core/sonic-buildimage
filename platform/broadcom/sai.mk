BRCM_SAI = libsaibcm_3.5.2.1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5s/libsaibcm_3.5.2.1_amd64.deb?sv=2015-04-05&sr=b&sig=VsOGePXPU9TtxXxQTkLfM%2FIzW6BL8q6RxP6QputuuEU%3D&se=2156-03-28T05%3A37%3A02Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.5.2.1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5s/libsaibcm-dev_3.5.2.1_amd64.deb?sv=2015-04-05&sr=b&sig=3pWbROLKK5ZuVcAra%2BYo1pk4B0k1P3C76wVw4KiqOtY%3D&se=2156-03-28T05%3A35%3A35Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

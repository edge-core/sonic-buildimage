BRCM_SAI = libsaibcm_3.3.4.3-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm_3.3.4.3-2_amd64.deb?sv=2015-04-05&sr=b&sig=GO2B4zoVJi0j0%2FZKbf8yhRL0oQ3clJEZFiy2AC14xSc%3D&se=2032-10-20T20%3A38%3A13Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.3.4.3-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm-dev_3.3.4.3-2_amd64.deb?sv=2015-04-05&sr=b&sig=aYEpjYMEIqfMnAiraXr9K%2FspEb8d2qGdwcIBxO3%2BjjY%3D&se=2032-10-20T20%3A37%3A51Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

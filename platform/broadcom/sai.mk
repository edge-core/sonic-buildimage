BRCM_SAI = libsaibcm_3.7.3.3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.3.3_amd64.deb?sv=2015-04-05&sr=b&sig=Y66VSRUEl4PDf5kHRo%2FS3DBBE9tONSyCzNJvi8IP9n8%3D&se=2033-08-25T01%3A22%3A08Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.7.3.3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.3.3_amd64.deb?sv=2015-04-05&sr=b&sig=6%2BWzgFL845H9lKE0COsN53P4MO4UWfSo0z%2FmUMFbYVk%3D&se=2033-08-25T01%3A21%3A50Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
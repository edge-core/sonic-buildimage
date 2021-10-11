BRCM_SAI = libsaibcm_3.5.3.7-6_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm_3.5.3.7-6_amd64.deb?sv=2019-10-10&st=2021-09-23T23%3A20%3A57Z&se=2040-09-24T23%3A20%3A00Z&sr=b&sp=r&sig=zYE0zYDSvshvDaBsmxgXnZlw2XuGMbN%2FKQ7Wdx5mr44%3D"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.7-6_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm-dev_3.5.3.7-6_amd64.deb?sv=2019-10-10&st=2021-09-23T23%3A22%3A10Z&se=2040-09-24T23%3A22%3A00Z&sr=b&sp=r&sig=GkqH6luvSrPBIukhGwlm7dKtiLja%2FQKVDrZ%2BDKt7OJk%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

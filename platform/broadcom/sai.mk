BRCM_SAI = libsaibcm_4.3.7.1-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.7.1-3_amd64.deb?sv=2020-08-04&st=2022-10-18T12%3A18%3A13Z&se=2037-10-19T12%3A18%3A00Z&sr=b&sp=r&sig=r78DbaCBmrQjGVQO84VUvAf%2BPHFeF6uTk%2Br7b2QwO4M%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.7.1-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.7.1-3_amd64.deb?sv=2020-08-04&st=2022-10-18T12%3A18%3A28Z&se=2037-10-19T12%3A18%3A00Z&sr=b&sp=r&sig=DjNdlKfDegvbc%2BLgADtr6Z69F5tYqxnYYoLQvvvN3mU%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

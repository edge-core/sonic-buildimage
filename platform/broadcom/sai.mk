BRCM_SAI = libsaibcm_3.5.3.8_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm_3.5.3.8_amd64.deb?sv=2019-10-10&st=2022-02-08T22%3A45%3A37Z&se=2037-02-09T22%3A45%3A00Z&sr=b&sp=r&sig=ilAmnbEhsCG2iI%2Bm3WBXBJ05lEU2xjoR5ef7ypN%2B%2F6c%3D"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.8_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm-dev_3.5.3.8_amd64.deb?sv=2019-10-10&st=2022-02-08T22%3A44%3A53Z&se=2037-02-09T22%3A44%3A00Z&sr=b&sp=r&sig=ZtrKEWVV9ds1EBPo0NwnzW9v39%2BNQhMlnn0qkBZWJ7o%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

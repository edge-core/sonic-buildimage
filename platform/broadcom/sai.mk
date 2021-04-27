BRCM_SAI = libsaibcm_4.3.3.5-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm_4.3.3.5-1_amd64.deb?sv=2019-12-12&st=2021-04-26T22%3A16%3A33Z&se=2030-04-27T22%3A16%3A00Z&sr=b&sp=r&sig=ssF1KPWFqoIsOsLOxwkYbzwsDF%2FNaZ8LfByjn%2BqGccU%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.3.5-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm-dev_4.3.3.5-1_amd64.deb?sv=2019-12-12&st=2021-04-26T22%3A17%3A56Z&se=2030-04-27T22%3A17%3A00Z&sr=b&sp=r&sig=2eWNoczh9P5c3Ir%2B1YL08ZkPol9GUkvNJKFGf%2BacXlI%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

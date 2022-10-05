BRCM_SAI = libsaibcm_4.3.7.1-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.7.1-1_amd64.deb?sv=2020-04-08&st=2022-10-05T01%3A58%3A26Z&se=2037-10-06T01%3A58%3A00Z&sr=b&sp=r&sig=wWW5cJ1RpH2NS%2Fz5LIMkuVKMAnw6nPMfR7Q9%2BqCG8ck%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.7.1-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.7.1-1_amd64.deb?sv=2020-04-08&st=2022-10-05T02%3A00%3A59Z&se=2037-10-06T02%3A00%3A00Z&sr=b&sp=r&sig=7AozOTdDhbjjc2ubXURoWG%2B9l6tqnRuoMOL%2FBYilDAc%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

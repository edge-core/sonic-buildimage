BRCM_SAI = libsaibcm_4.3.5.3-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.5.3-1_amd64.deb?sv=2020-08-04&st=2022-02-06T05%3A08%3A24Z&se=2030-02-07T05%3A08%3A00Z&sr=b&sp=r&sig=XXK7%2F1Qyc1aD%2FM29E6mOwyvyD8ARlZ67dVxhw6K56Ic%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.5.3-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.5.3-1_amd64.deb?sv=2020-08-04&st=2022-02-06T05%3A09%3A35Z&se=2030-02-07T05%3A09%3A00Z&sr=b&sp=r&sig=P0xG3DKNPFu2EY3toCqEvflxVE%2F1Ntbreas2YbH2Rqo%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

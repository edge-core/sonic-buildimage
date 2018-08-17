BRCM_SAI = libsaibcm_3.1.3.5-7_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.5-7_amd64.deb?sv=2015-04-05&sr=b&sig=0FaCT4a%2B07%2FkMIqZQF8NKk3UQL%2BU5M9icfe23F6rThY%3D&se=2155-07-10T08%3A53%3A11Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.5-7_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.5-7_amd64.deb?sv=2015-04-05&sr=b&sig=aTEosIZH90NExzK3opDzVFB%2FhWATEggoxKaTYudoR3I%3D&se=2155-07-10T08%3A53%3A39Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

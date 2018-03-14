BRCM_SAI = libsaibcm_3.1.3.4-5_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.4-5_amd64.deb?sv=2015-04-05&sr=b&sig=s757Jmeq0blUuQa%2BnWXfe80sChLHWAnuSDf2J84s4OE%3D&se=2031-11-16T21%3A58%3A22Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-5_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.4-5_amd64.deb?sv=2015-04-05&sr=b&sig=BOLw2xZ53Tp1JfBXZtqsKAltbYGTJuRV89Y9jDSSp50%3D&se=2031-11-16T21%3A56%3A19Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

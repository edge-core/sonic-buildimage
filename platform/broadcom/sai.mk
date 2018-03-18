BRCM_SAI = libsaibcm_3.1.3.4-7_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.4-7_amd64.deb?sv=2015-04-05&sr=b&sig=elzOgHCA3G8oKKMfWcbFa%2BvQzAh727mtYJnnVOzVJtY%3D&se=2155-02-07T23%3A37%3A54Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-7_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.4-7_amd64.deb?sv=2015-04-05&sr=b&sig=rysxdbCA%2BaqBgDnxztdRA2ixiME3ypqRvzyEds8hLw4%3D&se=2155-02-07T23%3A38%3A39Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

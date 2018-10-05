BRCM_SAI = libsaibcm_3.1.3.4-18_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.4-18_amd64.deb?sv=2015-04-05&sr=b&sig=FqiCA8J4cvVyaKG9VrA9HAh2TedtJHHQUmjXQOoxiJY%3D&se=2155-08-28T19%3A38%3A44Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-18_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.4-18_amd64.deb?sv=2015-04-05&sr=b&sig=kI7rK1xQ%2BkNePGDlagQgDCYmoBN%2By9Dn2UFnDAT34oA%3D&se=2155-08-28T19%3A42%3A49Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

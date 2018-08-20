BRCM_SAI = libsaibcm_3.1.3.4-16_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.4-16_amd64.deb?sv=2015-04-05&sr=b&sig=p7e4USdBWxIKYxP22t7yb%2BKtzlWBidZxQF1HZ%2FDs16I%3D&se=2155-07-13T04%3A43%3A02Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-16_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.4-16_amd64.deb?sv=2015-04-05&sr=b&sig=80iUtmr%2BbdWg7p5Zst%2FQrWuukgSx0TME2fRPPIhfLMQ%3D&se=2155-07-12T21%3A32%3A56Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

BRCM_SAI = libsaibcm_4.3.3.5-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.3.5-3_amd64.deb?sv=2015-04-05&sr=b&sig=EqEEo7pUSwkzxVidHnbSlENWyJQkqWZZ4JLN%2B1JZsBY%3D&se=2035-02-03T05%3A58%3A49Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.3.5-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.3.5-3_amd64.deb?sv=2015-04-05&sr=b&sig=JDFMqPxyb8bJlRG0UFQtpQ3opmP%2FQt%2F08PlMn1RXN%2F4%3D&se=2035-02-03T05%3A59%3A23Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

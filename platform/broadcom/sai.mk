BRCM_SAI = libsaibcm_3.1.3.4-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.4-1_amd64.deb?sv=2015-04-05&sr=b&sig=og1GOWhY9aScmFlWQT%2F51Nno%2FDGMZgxVbprQAaZyQVk%3D&se=2031-10-31T03%3A38%3A38Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.4-1_amd64.deb?sv=2015-04-05&sr=b&sig=lD1%2FLriHW9yPV9OAX9nqYJDwBm7B6Ge77WGcQvnPjAQ%3D&se=2031-10-31T03%3A37%3A55Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

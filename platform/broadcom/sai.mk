BRCM_SAI = libsaibcm_2.0.3.7_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.0.3.7_amd64.deb?sv=2015-04-05&sr=b&sig=3S9pY5Allql4fguipFdilJ%2BzP%2Ff4dvUFe3mNY3uhCIc%3D&se=2030-09-02T21%3A43%3A38Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.0.3.7_amd64.deb

$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))

$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.0.3.7_amd64.deb?sv=2015-04-05&sr=b&sig=KI8DfgGW8%2BOoZL6tJ9aJa%2F3RvHi%2FXD8gtOcDUD5nOPA%3D&se=2030-09-03T04%3A52%3A41Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)

$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

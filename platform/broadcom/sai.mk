BRCM_SAI = libsaibcm_3.7.5.1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.5.1_amd64.deb?sv=2015-04-05&sr=b&sig=baLk8LLHxk9CN%2Fu0rOar5ELvojYxD00DEcFcbCnFD%2BA%3D&se=2034-02-12T01%3A20%3A05Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.5.1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.5.1_amd64.deb?sv=2015-04-05&sr=b&sig=28n0jOPdv6r%2FhyQNXtufNdd9PEoA3WT5e1rCXs5cE58%3D&se=2034-02-12T01%3A20%3A56Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

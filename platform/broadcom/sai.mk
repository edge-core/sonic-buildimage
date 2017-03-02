BRCM_SAI = libsaibcm_2.1.3.1-4+0-20170301222525.13-1.gbp8d6580_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.3.1-4+0-20170301222525.13-1.gbp8d6580_amd64.deb?sv=2015-04-05&sr=b&sig=YhWQFb2Bz5ZgqyA8VciIT20I%2BBDhps77ksakG0jU92A%3D&se=2030-11-08T22%3A34%3A36Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.3.1-4+0-20170301222525.13-1.gbp8d6580_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.3.1-4+0-20170301222525.13-1.gbp8d6580_amd64.deb?sv=2015-04-05&sr=b&sig=QUmwuM3AZ4qe5sVFTmB6tEWApJKWU7PP5kfaDVM2dKU%3D&se=2030-11-08T22%3A35%3A34Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

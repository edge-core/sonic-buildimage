BRCM_SAI = libsaibcm_4.3.3.1-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm_4.3.3.1-1_amd64.deb?sv=2015-04-05&sr=b&sig=n7KoEZ5wXY%2FobPAy62d9C%2BKyAkKo4PIdIAWwqnDBm3E%3D&se=2034-11-14T03%3A30%3A33Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.3.1-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm-dev_4.3.3.1-1_amd64.deb?sv=2015-04-05&sr=b&sig=EavLNMXA6OS3s9oD34bKbdtfYHppR4egkh7V7jc4gWM%3D&se=2034-11-14T03%3A31%3A04Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

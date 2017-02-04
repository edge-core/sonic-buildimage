BRCM_SAI = libsaibcm_2.1.3.1+0-20170203082839.11-1.gbp995de3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.3.1+0-20170203082839.11-1.gbp995de3_amd64.deb?sv=2015-04-05&sr=b&sig=q%2Byg1WtnhhGHBeOjyO7LfMZejwqER%2F7Hdr%2F%2Bxs%2FUFSA%3D&se=2030-10-13T19%3A49%3A10Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.3.1+0-20170203082839.11-1.gbp995de3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.3.1+0-20170203082839.11-1.gbp995de3_amd64.deb?sv=2015-04-05&sr=b&sig=ihcuduBFhzV5yj%2F2kI%2BzTshm85KFtm2XGqHcXo%2FwD5U%3D&se=2030-10-13T19%3A50%3A07Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

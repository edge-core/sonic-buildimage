BRCM_SAI = libsaibcm_3.7.5.1-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/master/libsaibcm_3.7.5.1-2_amd64.deb?sv=2015-04-05&sr=b&sig=Ir7VDgFPOs4mU0k%2Fu76shUBpysh46Q1Btt0i%2FdhM0Ig%3D&se=2034-04-14T01%3A19%3A11Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.5.1-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/master/libsaibcm-dev_3.7.5.1-2_amd64.deb?sv=2015-04-05&sr=b&sig=sBiXxx2vncp0GLHIPx4IyiJQBqFV%2BGWUmdr7ccrnsT4%3D&se=2034-04-14T01%3A18%3A39Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

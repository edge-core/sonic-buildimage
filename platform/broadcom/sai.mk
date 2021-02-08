BRCM_SAI = libsaibcm_4.3.0.10-5_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm_4.3.0.10-5_amd64.deb?sv=2019-12-12&st=2021-02-08T00%3A20%3A49Z&se=2030-02-09T00%3A20%3A00Z&sr=b&sp=r&sig=rEpcTHNsSr10rKhpr6Cx3EFNa2dRE7VLP7ybZijQKpE%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.0.10-5_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm-dev_4.3.0.10-5_amd64.deb?sv=2019-12-12&st=2021-02-08T00%3A21%3A42Z&se=2030-02-09T00%3A21%3A00Z&sr=b&sp=r&sig=gvDnVYkQe%2FA2Yqw9p404Vtmx%2Fo8NwJMFoCn7K4W1k0M%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

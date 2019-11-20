BRCM_SAI = libsaibcm_3.5.3.3-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm_3.5.3.3-1_amd64.deb?sv=2015-04-05&sr=b&sig=ZRpT%2BiP%2BiaBJzTdb4ho%2F1FkH%2Bwc%2B9xwiQf2fsRQKe0Y%3D&se=2033-07-26T04%3A26%3A34Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.3-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm-dev_3.5.3.3-1_amd64.deb?sv=2015-04-05&sr=b&sig=yblqGyx256cZXEsn3pp0Pz94srsz%2BwPys9wZB0TMM3o%3D&se=2033-07-26T04%3A26%3A13Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

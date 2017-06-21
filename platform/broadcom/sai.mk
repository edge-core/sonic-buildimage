BRCM_SAI = libsaibcm_2.1.5.1-12-20170607194342.44_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-12-20170607194342.44_amd64.deb?sv=2015-04-05&sr=b&sig=gJJVxVT2o%2Bm14%2BwCBYFmBfcrDCzBA4b4iSmDKxnS13o%3D&se=2031-02-26T17%3A39%3A50Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-12-20170607194342.44_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-12-20170607194342.44_amd64.deb?sv=2015-04-05&sr=b&sig=AfYK3Qz%2FTV61E89u0kASm7wF3LEiqaZb%2Fde2jvbw9yk%3D&se=2031-02-26T17%3A40%3A14Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

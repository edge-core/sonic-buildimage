BRCM_SAI = libsaibcm_2.1.5.1-9-20170531184746.41_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-9-20170531184746.41_amd64.deb?sv=2015-04-05&sr=b&sig=VD4QFYR4J5nJPdS6ZHyfKbdroTILV%2Fz6s%2F251NWpyaE%3D&se=2031-02-08T18%3A26%3A35Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-9-20170531184746.41_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-9-20170531184746.41_amd64.deb?sv=2015-04-05&sr=b&sig=baUDbmm7PzF7Y7Y8Lz%2B759Xl1vhOkcnPBcqd6ZWWwSA%3D&se=2031-02-08T18%3A26%3A58Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

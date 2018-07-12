BRCM_SAI = libsaibcm_3.1.3.5-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.5-2_amd64.deb?sv=2015-04-05&sr=b&sig=wAXRViJp5SZtlHqEZVeAHZ0b%2F8Cfxw0QIjCaAigWS2s%3D&se=2032-03-19T18%3A25%3A07Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.5-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.5-2_amd64.deb?sv=2015-04-05&sr=b&sig=1LqBLe%2BPNHyVmcaes21TMuZ8VoUS%2FDIuGS5Vzn9N8L4%3D&se=2032-03-19T18%3A25%3A53Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

BRCM_SAI = libsaibcm_2.1.3.1-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.3.1-2_amd64.deb?sv=2015-04-05&sr=b&sig=zR%2BANpuGPa6oQoYTE20eeFEWXH7QugPV8f%2BPl8N5Y5Y%3D&se=2030-11-03T11%3A18%3A37Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.3.1-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.3.1-2_amd64.deb?sv=2015-04-05&sr=b&sig=H25Jlxwkacnm1agUykzHxcr4G2quJNRQVPVwrG623vQ%3D&se=2030-11-03T11%3A20%3A56Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

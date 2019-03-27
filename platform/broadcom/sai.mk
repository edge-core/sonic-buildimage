BRCM_SAI = libsaibcm_3.1.3.4-20_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.4-20_amd64.deb?sv=2015-04-05&sr=b&sig=r5ezPQ1tNe53icqTFio2dpE2it2XKPTk5kv4LcEA4gs%3D&se=2032-12-02T18%3A10%3A05Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-20_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.4-20_amd64.deb?sv=2015-04-05&sr=b&sig=VFbXjNqtnZTNk7ffwcmjPjeXakXmJL4hozjlyNhT%2F3A%3D&se=2032-12-02T18%3A10%3A28Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

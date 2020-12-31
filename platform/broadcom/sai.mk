BRCM_SAI = libsaibcm_3.7.5.2-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.5.2-1_amd64.deb?sv=2015-04-05&sr=b&sig=%2FHUrjpYZ0MPspo4jBc08d4pn4AWVS6%2Be3BID5qPNvs0%3D&se=2034-09-08T18%3A09%3A54Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.5.2-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.5.2-1_amd64.deb?sv=2015-04-05&sr=b&sig=qbyqn%2F9ueIH1ffWMjbhbUn15RRgt%2BFpvpFUOlspXkqs%3D&se=2034-09-08T18%3A10%3A31Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

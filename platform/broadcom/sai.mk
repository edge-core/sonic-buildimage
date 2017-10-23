BRCM_SAI = libsaibcm_3.0.3.2-9_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.2-9_amd64.deb?sv=2015-04-05&sr=b&sig=w4MY%2FMlnCe59xwMXRxODyLkaEDLEljeBlT3bPUnedoU%3D&se=2031-07-02T20%3A17%3A33Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.2-9_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.2-9_amd64.deb?sv=2015-04-05&sr=b&sig=zfBAMJKd0LUesg88UjDdUor%2Bc4j8omvw08MKymQQFnE%3D&se=2031-07-02T20%3A17%3A10Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
